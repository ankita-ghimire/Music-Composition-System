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
    from main import main_test as generate_cli # Renaming for clarity
    from melody_generator import MelodyGenerator
    from chord_generator import generate_chords
    from exporter import export_composition
    import database_manager as db
except ImportError as e:
    print(f"FATAL Error: Could not import a required module: {e}")
    sys.exit(1)

# --- Flask App Initialization ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key_change_this'
app.config['OUTPUT_FOLDER'] = os.path.join(backend_path, 'output')
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

db.create_database()
melody_engine = None 

@app.before_request
def initialize_model():
    """Initialize and train the AI model once when the server first starts."""
    global melody_engine
    print("Initializing and training AI model for the web server...")
    melody_engine = MelodyGenerator()
    training_data_path = Path(__file__).parent.parent / "training_data"
    melody_engine.train(str(training_data_path))
    print("AI model ready.")

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

@app.route("/my-compositions")
def my_compositions():
    if 'user_id' not in session:
        flash("Please log in to view your compositions.", "warning")
        return redirect(url_for('login'))
    user_compositions = db.load_compositions_for_user(session['user_id'])
    return render_template("my_compositions.html", compositions=user_compositions)

# ... other page routes ...
@app.route("/explore")
def explore(): return render_template("explore.html")
@app.route("/about")
def about(): return render_template("about.html")

# ... user auth routes ...
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if db.get_user_by_username(username): flash("Username already exists.", "warning")
        elif db.create_user(username, password):
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for('login'))
        else: flash("An error occurred. Please try again.", "danger")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = db.get_user_by_username(username)
        if user and check_password_hash(user[2], password):
            session['user_id'], session['username'] = user[0], user[1]
            return redirect(url_for('home'))
        else: flash("Invalid username or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

# ==============================================================================
# Functional Routes
# ==============================================================================
@app.route("/compose-action", methods=["POST"])
def compose_action():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Authentication required."}), 401
    
    try:
        data = request.form
        key_root, user_mode, num_bars, instrument, mood, tempo = \
            data.get("key_name", "C"), data.get("mode", "major"), int(data.get("num_bars", 4)), \
            data.get("instrument", "salamander-piano"), data.get("mood", "default"), int(data.get("tempo", 120))

        final_mode = user_mode
        if mood == "happy": final_mode = "major"
        elif mood == "sad": final_mode = "minor"
        key_name = key_root.upper() if final_mode == "major" else key_root.lower()
        
        composition_name = f"Web Piece ({mood.title()}) in {key_root} {final_mode}"

        melody_stream = melody_engine.generate(length=num_bars * 4, key=key_name, mood=mood)
        chord_stream = generate_chords(key_root, final_mode, num_bars, mood=mood)
        
        midi_filepath, _ = export_composition(
            melody_stream, chord_stream, Path(app.config['OUTPUT_FOLDER']), composition_name, instrument, tempo)
        if not midi_filepath: raise Exception("Exporter failed to create file.")
        
        base_filename = os.path.basename(midi_filepath)

        return jsonify({
            "success": True,
            "composition_details": { "title": composition_name, "key": key_root, "mode": user_mode, 
                                     "bars": num_bars, "filename": base_filename, "instrument": instrument, "mood": mood },
            "download_url": f"/download/{base_filename}",
            "midi_data_url": f"/midi-data/{base_filename}"
        })
    except Exception as e:
        print(f"SERVER ERROR in /compose-action: {e}")
        return jsonify({"success": False, "error": "An error occurred during composition."}), 500

@app.route("/save-composition", methods=["POST"])
def save_composition_action():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Authentication required."}), 401
    
    try:
        data = request.json
        # This function signature now matches your database_manager.py
        db.save_composition(
            user_id=session['user_id'], title=data['title'], melody_events="N/A", chord_names="N/A", 
            key=data['key'], mode=data['mode'], instrument=data['instrument'], mood=data['mood'], 
            bars=data['bars'], filename=data['filename']
        )
        return jsonify({"success": True, "message": "Composition saved!"})
    except Exception as e:
        print(f"SERVER ERROR in /save-composition: {e}")
        return jsonify({"success": False, "error": "Failed to save composition."}), 500

# ... (download and midi-data routes) ...
@app.route("/midi-data/<filename>")
def midi_data(filename): return send_from_directory(app.config['OUTPUT_FOLDER'], filename)
@app.route("/download/<filename>")
def download_file(filename): return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)