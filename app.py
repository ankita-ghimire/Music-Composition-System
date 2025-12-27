import os, sys, json
from flask import Flask, render_template, request, send_from_directory, jsonify, session, redirect, url_for, flash
from werkzeug.security import check_password_hash
from pathlib import Path
from music21 import chord

# --- Backend Setup ---
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if backend_path not in sys.path: sys.path.insert(0, backend_path)
try:
    from melody_generator import MelodyGenerator
    from chord_generator import generate_chords, create_stream_from_custom_progression
    from exporter import export_solo_composition, export_ensemble_composition, export_custom_composition
    from arranger import create_arpeggiated_accompaniment
    import database_manager as db
except ImportError as e:
    print(f"FATAL Error: Could not import a required module from 'src': {e}"); sys.exit(1)

# --- App and AI Initialization ---
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'your_super_secret_key_change_this'
app.config['OUTPUT_FOLDER'] = os.path.abspath(os.path.join(backend_path, 'output'))
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
db.create_database()
melody_engine = MelodyGenerator()
training_data_path = Path(__file__).parent.parent / "training_data"
if training_data_path.exists():
    melody_engine.train(str(training_data_path))
    print("AI model ready.")
else:
    print("FATAL Error: training_data folder not found.")

@app.route("/")
def home(): return render_template("home.html")

@app.route("/compose")
def compose_page():
    if 'user_id' not in session: flash("Please log in.", "warning"); return redirect(url_for('login'))
    return render_template("compose.html")


@app.route("/ensemble")
def ensemble_page():
    if 'user_id' not in session: flash("Please log in.", "warning"); return redirect(url_for('login'))
    return render_template("ensemble.html")

@app.route("/custom")
def custom_page():
    if 'user_id' not in session: flash("Please log in.", "warning"); return redirect(url_for('login'))
    return render_template("custom.html")

@app.route("/my-compositions")
def my_compositions():
    if 'user_id' not in session: flash("Please log in.", "warning"); return redirect(url_for('login'))
    user_compositions = db.load_compositions_for_user(session['user_id'])
    return render_template("my_compositions.html", compositions=user_compositions)

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
    session.clear(); flash("You have been logged out.", "info"); return redirect(url_for('home'))

@app.route("/compose-action", methods=["POST"])
def compose_action():
    if 'user_id' not in session: return jsonify({"success": False, "error": "Authentication required."}), 401
    try:
        data = request.form
        key_root, user_mode, num_bars, instrument, mood, tempo_bpm = \
            data.get("key_name", "C"), data.get("mode", "major"), int(data.get("num_bars", 4)), \
            data.get("instrument", "salamander-piano"), data.get("mood", "default"), int(data.get("tempo", 120))
        final_mode = user_mode; temperature = 1.2
        if mood == "happy": final_mode = "major"; temperature = 1.0
        elif mood == "sad": final_mode = "minor"; temperature = 0.8
        key_name = key_root.upper() if final_mode == "major" else key_root.lower()
        composition_name = f"Solo Piece ({mood.title()}) in {key_root} {final_mode}"
        
        melody_stream = melody_engine.generate(length=num_bars * 4, key=key_name, temperature=temperature, mood=mood)
        chord_stream = generate_chords(key_root, final_mode, num_bars, mood=mood)
        
        output_folder = Path(app.config['OUTPUT_FOLDER'])
        midi_filepath, xml_filepath = export_solo_composition(melody_stream, chord_stream, output_folder, composition_name, instrument, tempo_bpm)
        if not midi_filepath: raise Exception("Exporter failed.")
        
        base_midi_filename = os.path.basename(midi_filepath)
        base_xml_filename = os.path.basename(xml_filepath)
        
        
      
        return jsonify({
            "success": True,
            "composition_details": { 
                "title": composition_name, "key": key_root, "mode": final_mode, "bars": num_bars,
                "instrument": instrument, "mood": mood, 
                "filename_midi": base_midi_filename, "filename_xml": base_xml_filename
            },
            "download_url_midi": f"/download/{base_midi_filename}",
            "download_url_xml": f"/download/{base_xml_filename}",
            "midi_data_url": f"/midi-data/{base_midi_filename}" # Use the new midi-data route
        })
    except Exception as e:
        print(f"SERVER ERROR in /compose-action: {e}"); import traceback; traceback.print_exc()
        return jsonify({"success": False, "error": "An error occurred."}), 500

@app.route("/save-composition", methods=["POST"])
def save_composition_action():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Authentication required."}), 401
    try:
        data = request.json # Get the data the JavaScript sent
        
        db.save_solo_composition(
            user_id=session['user_id'],
            title=data['title'],
            key=data['key'],
            mode=data['mode'],
            bars=data['bars'],
            instrument=data['instrument'],
            filename_midi=data['filename_midi'],
            filename_xml=data['filename_xml'],
            mood=data['mood']
        )
        return jsonify({"success": True, "message": "Composition saved successfully!"})
    except Exception as e:
        print(f"SERVER ERROR in /save-composition: {e}")
        return jsonify({"success": False, "error": "Failed to save composition."}), 500
@app.route("/ensemble-action", methods=["POST"])
def ensemble_action():
    if 'user_id' not in session: return jsonify({"success": False, "error": "Authentication required."}), 401
    try:
        data = request.form
        key_root, user_mode, num_bars, lead_instrument, accomp_instrument, mood, tempo_bpm = \
            data.get("key_name", "C"), data.get("mode", "major"), int(data.get("num_bars", 4)), \
            data.get("lead_instrument", "flute"), data.get("accomp_instrument", "guitar-acoustic"), \
            data.get("mood", "default"), int(data.get("tempo", 120))
        final_mode = user_mode; temperature = 1.2
        if mood == "happy": final_mode = "major"; temperature = 1.0
        elif mood == "sad": final_mode = "minor"; temperature = 0.8
        key_name = key_root.upper() if final_mode == "major" else key_root.lower()
        composition_name = f"Ensemble Piece ({mood.title()}) in {key_root} {final_mode}"
        
        melody_stream = melody_engine.generate(length=num_bars * 4, key=key_name, temperature=temperature, mood=mood)
        chord_stream = generate_chords(key_root, final_mode, num_bars, mood=mood)
        accomp_stream = create_arpeggiated_accompaniment(chord_stream)
        
        output_folder = Path(app.config['OUTPUT_FOLDER'])
        midi_filepath, xml_filepath = export_ensemble_composition(melody_stream, accomp_stream, output_folder, composition_name, lead_instrument, accomp_instrument, tempo_bpm)
        if not midi_filepath: raise Exception("Ensemble exporter failed.")
        
        base_midi_filename = os.path.basename(midi_filepath)
        base_xml_filename = os.path.basename(xml_filepath)
        
        return jsonify({
            "success": True,
            "composition_details": {
                "title": composition_name, "key": key_root, "mode": final_mode, "mood": mood, "bars": num_bars,
                "lead_instrument": lead_instrument, "accomp_instrument": accomp_instrument,
                "filename_midi": base_midi_filename, "filename_xml": base_xml_filename
            },
            "download_url_midi": f"/download/{base_midi_filename}",
            "download_url_xml": f"/download/{base_xml_filename}",
            # --- THIS LINE IS THE FIX ---
            "midi_data_url": f"/midi-data/{base_midi_filename}" 
        })
    except Exception as e:
        print(f"SERVER ERROR in /ensemble-action: {e}"); return jsonify({"success": False, "error": "An error occurred."}), 500

@app.route("/save-ensemble-composition", methods=["POST"])
def save_ensemble_composition_action():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Authentication required."}), 401
    try:
        data = request.json
        db.save_ensemble_composition(
            user_id=session['user_id'],
            title=data['title'],
            key=data['key'],
            mode=data['mode'],
            mood=data['mood'],
            bars=data['bars'],
            lead_instrument=data['lead_instrument'],
            accomp_instrument=data['accomp_instrument'],
            filename_midi=data['filename_midi'],
            filename_xml=data['filename_xml']
        )
        return jsonify({"success": True, "message": "Ensemble piece saved successfully!"})
    except Exception as e:
        print(f"SERVER ERROR in /save-ensemble-composition: {e}")
        return jsonify({"success": False, "error": "Failed to save ensemble piece."}), 500


@app.route("/custom-action", methods=["POST"])
def custom_action():
    if 'user_id' not in session: return jsonify({"success": False, "error": "Authentication required."}), 401
    try:
        data = request.form
        progression_str = data.get("chord_progression")
        instrument_name = data.get("instrument", "salamander-piano")
        tempo_bpm = int(data.get("tempo", 120))
        
        if not progression_str:
            return jsonify({"success": False, "error": "Chord progression is empty."})
        
        custom_chord_list = [c.strip() for c in progression_str.split(',')]
        custom_chord_stream = create_stream_from_custom_progression(custom_chord_list)
        
        analysis_key = custom_chord_stream.analyze('key')
        key_for_melody = analysis_key.tonic.name.upper() if analysis_key.mode == 'major' else analysis_key.tonic.name.lower()
        
        melody_stream = melody_engine.generate(length=len(custom_chord_list) * 4, key=key_for_melody)
        
        composition_name = f"Custom Piece in {analysis_key.name.capitalize()}"
        output_folder = Path(app.config['OUTPUT_FOLDER'])
        
        midi_filepath, xml_filepath = export_custom_composition(melody_stream, custom_chord_stream, output_folder, composition_name, instrument_name, tempo_bpm)
        if not midi_filepath: raise Exception("Custom exporter failed.")

        base_midi_filename = os.path.basename(midi_filepath)
        base_xml_filename = os.path.basename(xml_filepath)
        
        return jsonify({
            "success": True,
            "composition_details": {
                "title": composition_name, "key": analysis_key.tonic.name, "mode": analysis_key.mode,
                "bars": len(custom_chord_list), "instrument": instrument_name, "mood": "custom",
                "filename_midi": base_midi_filename, "filename_xml": base_xml_filename
            },
            "download_url_midi": f"/download/{base_midi_filename}",
            "download_url_xml": f"/download/{base_xml_filename}",
            "midi_data_url": f"/midi-data/{base_midi_filename}"
        })
    except Exception as e:
        print(f"SERVER ERROR in /custom-action: {e}"); import traceback; traceback.print_exc()
        return jsonify({"success": False, "error": "An error occurred during generation."}), 500


@app.route("/save-custom-composition", methods=["POST"])
def save_custom_composition_action():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Authentication required."}), 401
    try:
        data = request.json
        db.save_custom_composition(
            user_id=session['user_id'],
            title=data['title'],
            key=data['key'],
            mode=data['mode'],
            bars=data['bars'],
            instrument=data['instrument'],
            filename_midi=data['filename_midi'],
            filename_xml=data['filename_xml']
        )
        return jsonify({"success": True, "message": "Custom piece saved successfully!"})
    except Exception as e:
        print(f"SERVER ERROR in /save-custom-composition: {e}")
        return jsonify({"success": False, "error": "Failed to save custom piece."}), 500


@app.route("/midi-data/<filename>")
def midi_data(filename):
    """Serves the raw MIDI file data for the in-browser player."""
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)
# --- END OF FIX ---

@app.route("/play-midi/<int:comp_id>")
def play_midi_from_db(comp_id):
    if 'user_id' not in session: return "Unauthorized", 401
    composition = db.get_composition_by_id(comp_id, session['user_id'])
    if not composition: return "Not Found", 404
    return send_from_directory(app.config['OUTPUT_FOLDER'], composition['filename_midi'])

@app.route("/delete-composition/<int:comp_id>", methods=["POST"])
def delete_composition_action(comp_id):
    if 'user_id' not in session: return jsonify({"success": False, "error": "Authentication required."}), 401
    try:
        db.delete_composition(comp_id, session['user_id'])
        flash("Composition deleted successfully.", "success")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": "Failed to delete composition."}), 500

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)
# --- Server Execution ---
if __name__ == "__main__":
    app.run(debug=True)

