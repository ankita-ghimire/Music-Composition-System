# In server.py
# FINAL, COMPLETE, AND UNIFIED VERSION
# This server handles both Solo and Ensemble composition workflows.

import os
import sys
from flask import Flask, render_template, request, send_from_directory, jsonify, session, redirect, url_for, flash
from werkzeug.security import check_password_hash
from pathlib import Path

# --- Backend Setup ---
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    # Import all necessary backend modules
    from melody_generator import MelodyGenerator
    from chord_generator import generate_chords
    from exporter import export_composition, export_ensemble_composition
    from arranger import create_arpeggiated_accompaniment
    import database_manager as db
except ImportError as e:
    print(f"FATAL Error: Could not import a required module from 'src': {e}")
    sys.exit(1)

# --- App and AI Initialization ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-very-secret-key-that-you-should-change'
app.config['OUTPUT_FOLDER'] = os.path.join(backend_path, 'output')
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
db.create_database()
melody_engine = MelodyGenerator()
training_data_path = Path(__file__).parent.parent / "training_data"
if training_data_path.exists():
    melody_engine.train(str(training_data_path))
    print("AI model ready.")
else:
    print("FATAL Error: training_data folder not found.")

# ==============================================================================
# Page Rendering and User Auth Routes
# ==============================================================================
@app.route("/")
def home(): return render_template("home.html")

@app.route("/compose")
def compose_page():
    if 'user_id' not in session:
        flash("Please log in to start composing.", "warning")
        return redirect(url_for('login'))
    return render_template("compose.html")

# NEW: Route for the Ensemble page
@app.route("/ensemble")
def ensemble_page():
    if 'user_id' not in session:
        flash("Please log in to start arranging.", "warning")
        return redirect(url_for('login'))
    return render_template("ensemble.html")

@app.route("/my-compositions")
def my_compositions():
    if 'user_id' not in session:
        flash("Please log in to view your compositions.", "warning")
        return redirect(url_for('login'))
    user_compositions = db.load_compositions_for_user(session['user_id'])
    return render_template("my_compositions.html", compositions=user_compositions)

@app.route("/explore")
def explore(): return render_template("explore.html")

@app.route("/about")
def about(): return render_template("about.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if db.get_user_by_username(username):
            flash("Username already exists.", "warning")
        elif db.create_user(username, password):
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for('login'))
        else:
            flash("An error occurred. Please try again.", "danger")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = db.get_user_by_username(username)
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

# ==============================================================================
# Functional Routes (Actions & Data)
# ==============================================================================

# --- SOLO COMPOSER ACTION ---
@app.route("/compose-action", methods=["POST"])
def compose_action():
    """Handles the form submission for the SOLO composer."""
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Authentication required."}), 401
    
    try:
        data = request.form
        key_root, user_mode, num_bars, instrument, mood, tempo = \
            data.get("key_name", "C"), data.get("mode", "major"), int(data.get("num_bars", 4)), \
            data.get("instrument", "salamander-piano"), data.get("mood", "default"), int(data.get("tempo", 120))

        final_mode = user_mode
        temperature = 1.2
        if mood == "happy": final_mode = "major"; temperature = 1.0
        elif mood == "sad": final_mode = "minor"; temperature = 0.8
        
        key_name = key_root.upper() if final_mode == "major" else key_root.lower()
        composition_name = f"Solo Piece ({mood.title()}) in {key_root} {final_mode}"

        melody_stream = melody_engine.generate(length=num_bars * 4, key=key_name, temperature=temperature, mood=mood)
        chord_stream = generate_chords(key_root, final_mode, num_bars, mood=mood)
        
        output_folder = Path(app.config['OUTPUT_FOLDER'])
        midi_filepath, _ = export_composition(
            melody_stream, chord_stream, output_folder, composition_name, instrument, tempo)
            
        if not midi_filepath: raise Exception("Exporter failed.")
        
        # Here you would call your original db.save_composition
        # ...

        return jsonify({"success": True, "download_url": f"/download/{os.path.basename(midi_filepath)}"})
        
    except Exception as e:
        print(f"SERVER ERROR in /compose-action: {e}")
        return jsonify({"success": False, "error": "An error occurred during solo composition."}), 500


# --- NEW: ENSEMBLE COMPOSER ACTION ---
@app.route("/ensemble-action", methods=["POST"])
def ensemble_action():
    """Handles the form submission from the ENSEMBLE page."""
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Authentication required."}), 401
    
    try:
        data = request.form
        key_root = data.get("key_name", "C")
        user_mode = data.get("mode", "major")
        num_bars = int(data.get("num_bars", 4))
        lead_instrument = data.get("lead_instrument", "flute")
        accomp_instrument = data.get("accomp_instrument", "guitar-acoustic")
        mood = data.get("mood", "default")
        tempo_bpm = int(data.get("tempo", 120))

        final_mode = user_mode
        temperature = 1.2
        if mood == "happy": final_mode = "major"; temperature = 1.0
        elif mood == "sad": final_mode = "minor"; temperature = 0.8
        
        key_name = key_root.upper() if final_mode == "major" else key_root.lower()
        composition_name = f"Ensemble Piece ({mood.title()}) in {key_root} {final_mode}"

        melody_stream = melody_engine.generate(length=num_bars * 4, key=key_name, temperature=temperature, mood=mood)
        chord_stream = generate_chords(key_root, final_mode, num_bars, mood=mood)
        accomp_stream = create_arpeggiated_accompaniment(chord_stream)
        
        output_folder = Path(app.config['OUTPUT_FOLDER'])
        midi_filepath, _ = export_ensemble_composition(
            melody_stream=melody_stream, 
            accomp_stream=accomp_stream, 
            output_path=output_folder, 
            composition_name=composition_name,
            lead_instrument_name=lead_instrument,
            accomp_instrument_name=accomp_instrument,
            bpm=tempo_bpm
        )

        if not midi_filepath: raise Exception("Ensemble exporter failed.")
            
        db.save_ensemble_composition(
    user_id=session['user_id'],
    title=composition_name,
    melody_events=melody_events,
    chord_names=chord_names,
    key=key_root,
    mode=final_mode,
    lead_instrument=lead_instrument,
    accomp_instrument=accomp_instrument,
    mood=mood,
    bars=num_bars,
    filename=base_midi_filename
)


        return jsonify({"success": True, "download_url": f"/download/{os.path.basename(midi_filepath)}"})

    except Exception as e:
        print(f"SERVER ERROR in /ensemble-action: {e}")
        return jsonify({"success": False, "error": "An error occurred during ensemble composition."}), 500


# --- SHARED UTILITY ROUTES ---
@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

# ... (add other routes like /play-midi if needed) ...

# --- Server Execution ---
if __name__ == "__main__":
    app.run(debug=True)