# In src/test_ensemble.py
# A dedicated script for testing the complete multi-instrument ensemble pipeline.

import os
import sys
from pathlib import Path

# --- Make sure other src files are discoverable ---
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# --- Import all the necessary modules ---
from melody_generator import MelodyGenerator
from chord_generator import generate_chords
# Import the NEW ensemble-specific exporter
from exporter import export_ensemble_composition
# Import the NEW arranger module
from arranger import create_arpeggiated_accompaniment
# We can re-use the file opener from main.py for convenience
from main import open_in_musescore


def run_ensemble_test():
    """
    A runnable function for testing the full ENSEMBLE AI pipeline,
    from user input to final score generation.
    """
    print("=== Music Composition System (Ensemble Backend Test) ===\n")
    
    # 1. Get all necessary user inputs for the ensemble feature
    key_root = input("Enter Key (e.g., C): ").strip()
    user_mode = input("Enter Mode (major/minor): ").strip().lower()
    lead_instrument = input("Enter Lead Instrument (flute, violin, piano, guitar-acoustic): ").strip().lower()
    accomp_instrument = input("Enter Accompaniment Instrument (guitar-acoustic, piano): ").strip().lower()
    mood = input("Enter Mood (default, happy, sad): ").strip().lower()
    num_bars = int(input("Enter Number of Bars (e.g., 8): ").strip())
    tempo_bpm = int(input("Enter Tempo (BPM, e.g., 120): ").strip())

    # 2. Adjust parameters based on mood (same logic as server.py)
    final_mode = user_mode
    temperature = 1.2
    if mood == "happy": final_mode = "major"; temperature = 1.0
    elif mood == "sad": final_mode = "minor"; temperature = 0.8
    
    key_name = key_root.upper() if final_mode == "major" else key_root.lower()
    composition_name = f"Ensemble Test ({mood.title()}) in {key_root.upper()} {final_mode}"
    print(f"\nParameters: Lead={lead_instrument}, Accomp={accomp_instrument}, Tempo={tempo_bpm} BPM")

    # 3. Initialize and Train the Melody AI
    print("\nInitializing and training AI model...")
    melody_engine = MelodyGenerator()
    training_data_path = Path(__file__).parent.parent / "training_data"
    melody_engine.train(str(training_data_path))

    # 4. Generate All Musical Parts in the correct order
    print(f"\nGenerating {num_bars}-bar piece...")
    # Generate the foundational chord progression first
    chord_stream = generate_chords(key_root, final_mode, num_bars, mood=mood)
    # Generate the lead melody
    melody_stream = melody_engine.generate(length=num_bars * 4, key=key_name, temperature=temperature, mood=mood)
    # Generate the accompaniment based on the chords
    accomp_stream = create_arpeggiated_accompaniment(chord_stream)
    print("-> All musical parts generated successfully.")

    # 5. Export the complete ensemble using the NEW exporter function
    output_folder = Path(__file__).parent.parent / "output"
    
    _, xml_filepath = export_ensemble_composition(
        melody_stream=melody_stream,
        accomp_stream=accomp_stream,
        output_path=output_folder,
        composition_name=composition_name,
        lead_instrument_name=lead_instrument,
        accomp_instrument_name=accomp_instrument,
        bpm=tempo_bpm
    )
    
    # 6. Open the final multi-instrument score in MuseScore
    if xml_filepath:
        print("\n--- Ensemble Backend Test Complete ---")
        open_in_musescore(xml_filepath)
    else:
        print("\n--- Ensemble Backend Test Failed: Could not generate music files. ---")

# This makes the script runnable from the terminal
if __name__ == "__main__":
    run_ensemble_test()