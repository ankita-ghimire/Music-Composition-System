import os
import sys
from flask import Flask, render_template, request, send_from_directory, jsonify, session, redirect, url_for, flash
from werkzeug.security import check_password_hash
from pathlib import Path
from unittest.mock import patch

# --- Backend Setup ---
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from main import main_test
    from melody_generator import MelodyGenerator
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

# ==============================================================================
# ONE-TIME SETUP
# ==============================================================================
@app.before_request
def initialize_model():
    """Initialize and train the AI model once when the server first starts."""
    global melody_engine
    if melody_engine is None:  # ✅ Prevent retraining on every request
        print("Initializing and training AI model for the web server...")
        melody_engine = MelodyGenerator()
        training_data_path = Path(__file__).parent.parent / "training_data"
        melody_engine.train(str(training_data_path))
        print("AI model ready.")

# ==============================================================================
# Page Rendering Routes
# ==============================================================================
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/compose")
def compose_page():
    if 'user_id' not in session:
        flash("Please log in to start composing.", "warning")
        return redirect(url_for('login'))
    return render_template("compose.html")

@app.route("/ensemble_page")
def ensemble_page():
    if 'user_id' not in session:
        flash("Please log in to create an ensemble piece.", "warning")
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
def explore():
    return render_template("explore.html")

@app.route("/about")
def about():
    return render_template("about.html")

# ==============================================================================
# User Authentication Routes
# ==============================================================================
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

@app.route("/custom_page")
def custom_page():
    return render_template("custom.html")

# ==============================================================================
# Functional Routes (For Generating and Saving Music)
# ==============================================================================
@app.route("/compose-action", methods=["POST"])
def compose_action():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Authentication required."}), 401
    
    try:
        data = request.form
        key_root = data.get("key_name", "C")
        user_mode = data.get("mode", "major")
        instrument = data.get("instrument", "piano")
        mood = data.get("mood", "default")
        num_bars = int(data.get("num_bars", 4))
        tempo_bpm = int(data.get("tempo", 120))
        
        # --- Patch input() for automation ---
        inputs = [key_root, user_mode, instrument, mood, str(num_bars), str(tempo_bpm)]
        with patch('builtins.input', side_effect=inputs):
            main_test(run_from_web=True)

        output_folder = Path(app.config['OUTPUT_FOLDER'])
        files = sorted(output_folder.glob('*.mid'), key=os.path.getmtime, reverse=True)
        if not files:
            raise Exception("main_test() did not generate an output MIDI file.")
        
        latest_midi_file = files[0]
        latest_xml_file = latest_midi_file.with_suffix('.mxl')

        db.save_composition(
            user_id=session['user_id'],
            title=latest_midi_file.stem,
            key=key_root, mode=user_mode, bars=num_bars,
            filename_midi=latest_midi_file.name, filename_xml=latest_xml_file.name,
            instrument=instrument, mood=mood,
            is_ensemble=0, accomp_instrument=None
        )
        
        return jsonify({
            "success": True,
            "composition_details": { "title": latest_midi_file.stem, "key": key_root, "mode": user_mode, 
                                     "bars": num_bars, "filename_midi": latest_midi_file.name, "filename_xml": latest_xml_file.name, 
                                     "instrument": instrument, "mood": mood, "is_ensemble": 0, "accomp_instrument": None },
            "download_url_midi": f"/download/{latest_midi_file.name}",
            "download_url_xml": f"/download/{latest_xml_file.name}",
            "midi_data_url": f"/midi-data/{latest_midi_file.name}"
        })
    except Exception as e:
        print(f"SERVER ERROR in /compose-action: {e}")
        return jsonify({"success": False, "error": "An error occurred during composition."}), 500

@app.route("/ensemble-action", methods=["POST"])
def ensemble_action():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Authentication required."}), 401
    
    try:
        data = request.form
        key_root = data.get("key_name", "C")
        user_mode = data.get("mode", "major")
        num_bars = int(data.get("num_bars", 4))
        lead_instrument = data.get("lead_instrument", "piano")
        accomp_instrument = data.get("accomp_instrument", "guitar")
        mood = data.get("mood", "default")

        # --- Patch input() for ensemble too ---
        inputs = [key_root, user_mode, lead_instrument, mood, str(num_bars), "120"]
        with patch('builtins.input', side_effect=inputs):
            main_test(run_from_web=True, is_ensemble=True, accomp_instrument=accomp_instrument)

        output_folder = Path(app.config['OUTPUT_FOLDER'])
        files = sorted(output_folder.glob('*.mid'), key=os.path.getmtime, reverse=True)
        if not files:
            raise Exception("main_test() did not generate an output MIDI file.")
        
        latest_midi_file = files[0]
        latest_xml_file = latest_midi_file.with_suffix('.mxl')

        db.save_composition(
            user_id=session['user_id'],
            title=f"Ensemble_{latest_midi_file.stem}",
            key=key_root, mode=user_mode, bars=num_bars,
            filename_midi=latest_midi_file.name, filename_xml=latest_xml_file.name,
            instrument=lead_instrument, mood=mood,
            is_ensemble=1, accomp_instrument=accomp_instrument
        )
        
        return jsonify({
            "success": True,
            "composition_details": { "title": f"Ensemble_{latest_midi_file.stem}", "key": key_root, "mode": user_mode, 
                                     "bars": num_bars, "filename_midi": latest_midi_file.name, "filename_xml": latest_xml_file.name, 
                                     "instrument": lead_instrument, "mood": mood, "is_ensemble": 1, "accomp_instrument": accomp_instrument },
            "download_url_midi": f"/download/{latest_midi_file.name}",
            "download_url_xml": f"/download/{latest_xml_file.name}",
            "midi_data_url": f"/midi-data/{latest_midi_file.name}"
        })
    except Exception as e:
        print(f"SERVER ERROR in /ensemble-action: {e}")
        return jsonify({"success": False, "error": "An error occurred during ensemble composition."}), 500

@app.route("/save-composition", methods=["POST"])
def save_composition_action():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Authentication required."}), 401
    try:
        data = request.json
        db.save_composition(
            user_id=session['user_id'], title=data['title'], key=data['key'], mode=data['mode'], 
            bars=data['bars'], filename_midi=data['filename_midi'], filename_xml=data['filename_xml'], 
            instrument=data['instrument'], mood=data['mood'], is_ensemble=data['is_ensemble'], 
            accomp_instrument=data['accomp_instrument']
        )
        return jsonify({"success": True, "message": "Composition saved!"})
    except Exception as e:
        print(f"SERVER ERROR in /save-composition: {e}")
        return jsonify({"success": False, "error": "Failed to save composition."}), 500

@app.route("/play-midi/<int:comp_id>")
def play_midi_from_db(comp_id):
    if 'user_id' not in session: return "Unauthorized", 401
    composition = db.get_composition_by_id(comp_id, session['user_id'])
    if not composition: return "Not Found", 404
    return send_from_directory(app.config['OUTPUT_FOLDER'], composition['filename_midi'])

@app.route("/midi-data/<filename>")
def midi_data(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

# ==============================================================================
# Server Execution
# ==============================================================================
if __name__ == "__main__":
    app.run(debug=True)
