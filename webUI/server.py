import os
import sys
from flask import Flask, render_template, request, send_from_directory, jsonify
from pathlib import Path

# --- Ensure backend (src/) is discoverable ---
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from main import generate_composition
except ImportError:
    print("Error: Could not import 'generate_composition' from 'src.main'.")
    sys.exit(1)

app = Flask(__name__)

# --- Configuration ---
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'output'))
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.config['OUTPUT_FOLDER'] = OUTPUT_DIR

# --- Page Rendering Routes ---

@app.route("/")
def home():
    """Renders the new welcome/landing page."""
    return render_template("home.html")

@app.route("/compose")
def compose_page():
    """Renders the music composition interface."""
    return render_template("compose.html")

@app.route("/explore")
def explore():
    """Renders the community exploration page."""
    return render_template("explore.html")

@app.route("/my-compositions")
def my_compositions():
    """Renders the user's personal compositions page."""
    return render_template("my_compositions.html")

@app.route("/about")
def about():
    """Renders the about page."""
    return render_template("about.html")

# --- Functional Routes (Actions & Data) ---

@app.route("/compose-action", methods=["POST"])
def compose_action():
    """Handles the form submission from the compose page and generates music."""
    try:
        key_name = request.form.get("key_name", "C")
        mode = request.form.get("mode", "major")
        num_bars = int(request.form.get("num_bars", 4))
        # Note: Tempo from the form is available via request.form.get("tempo")
        # You would need to pass this to your generate_composition function to use it.

        midi_filename, _ = generate_composition(key_name, mode, num_bars, auto_open=False)
        base_midi_filename = os.path.basename(midi_filename)

        return jsonify({
            "success": True,
            "midi_url": f"/download/{base_midi_filename}"
        })

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/download/<filename>")
def download_file(filename):
    """Serves the generated MIDI file for download."""
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)