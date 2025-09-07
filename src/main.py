# In src/main.py
# FINAL, COMPLETE, AND VERIFIED VERSION
import os
import sys
from pathlib import Path
import subprocess

# This ensures that all other files in the 'src' folder can be found
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from melody_generator import MelodyGenerator
from chord_generator import generate_chords
from exporter import export_composition

def open_in_musescore(file_path: str):
    """Helper function to automatically open the final score."""
    print(f"\nAttempting to open {os.path.basename(file_path)}...")
    if not file_path or not os.path.exists(file_path):
        print(f"⚠️ Error: File path is invalid. Cannot open.")
        return
    if sys.platform == "win32":
        possible_paths = [
            "C:/Program Files/MuseScore 4/bin/MuseScore4.exe",
            "C:/Program Files/MuseScore Studio/bin/MuseScore Studio.exe",
        ]
        for ms_path in possible_paths:
            if os.path.exists(ms_path):
                try:
                    subprocess.Popen([ms_path, file_path])
                    print(f"✅ Successfully launched MuseScore.")
                    return
                except Exception: continue
        try:
            os.startfile(file_path)
            print("✅ Opened file with default application.")
        except Exception as e:
            print(f"⚠️ Failed to open file with default app: {e}")
    else: # macOS / Linux
        try:
            subprocess.run(["open", file_path], check=True)
            print("✅ Opened file with default application.")
        except Exception:
            print(f"⚠️ Failed to open file.")

def main_test(run_from_web=False):
    """Final, runnable function for testing the full AI pipeline with all features."""
    print("=== Music Composition System (Full Backend Test) ===\n")
    
    key_root = input("Enter Key (e.g., C): ").strip()
    user_mode = input("Enter Mode (major/minor): ").strip().lower()
    instrument = input("Enter Instrument (piano, flute, violin): ").strip().lower()
    mood = input("Enter Mood (default, happy, sad): ").strip().lower()
    num_bars = int(input("Enter Number of Bars (e.g., 8): ").strip())
    tempo_bpm = int(input("Enter Tempo (BPM, e.g., 120): ").strip())

    final_mode = user_mode
    if mood == "happy": final_mode = "major"
    elif mood == "sad": final_mode = "minor"
    
    key_name_for_melody = key_root.upper() if final_mode == "major" else key_root.lower()
    composition_name = f"CLI Test ({mood.title()}) in {key_root.upper()} {final_mode}"
    print(f"\nParameters: Key={key_name_for_melody}, Instrument={instrument}, Tempo={tempo_bpm} BPM")

    print("\nInitializing and training AI model...")
    melody_engine = MelodyGenerator()
    training_data_path = Path(__file__).parent.parent / "training_data"
    melody_engine.train(str(training_data_path))

    print(f"\nGenerating {num_bars}-bar piece...")
    melody_stream = melody_engine.generate(length=num_bars * 4, key=key_name_for_melody, mood=mood)
    chord_stream = generate_chords(key_root, final_mode, num_bars, mood=mood)
    print("-> AI data generated successfully.")

    output_folder = Path(__file__).parent.parent / "output"
    
    midi_filepath, xml_filepath = export_composition(
        melody_stream=melody_stream,
        chord_stream=chord_stream,
        output_path=output_folder,
        composition_name=composition_name,
        instrument_name=instrument,
        bpm=tempo_bpm
    )
    
    if xml_filepath and not run_from_web:
        print("\n--- Backend Test Complete ---")
        open_in_musescore(xml_filepath)
    elif not xml_filepath:
        print("\n--- Backend Test Failed ---")

if __name__ == "__main__":
    main_test()