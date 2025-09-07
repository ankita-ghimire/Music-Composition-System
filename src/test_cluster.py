# In src/test_custom.py
# A NEW, dedicated script for testing the "Custom Progression" feature.
# It does not interfere with main.py or test_ensemble.py.

import os
import sys
from pathlib import Path
import json

# --- Make sure other src files are discoverable ---
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# --- Import modules ---
from melody_generator import MelodyGenerator
# We need NEW backend functions for this feature
from chord_generator import create_stream_from_custom_progression
from exporter import export_custom_composition # A new, dedicated exporter
# We can reuse the file opener
from main import open_in_musescore


def run_custom_test():
    """
    Tests the full CUSTOM PROGRESSION pipeline.
    """
    print("=== Music Composition System (Custom Progression Test) ===\n")
    
    # 1. Get User Input
    print("Enter your chord progression, separated by commas (e.g., Am, F, C, G)")
    user_input = input("Your Progression: ")
    custom_chord_list = [chord.strip() for chord in user_input.split(',')]
    if not custom_chord_list:
        print("Error: No chords entered."); return
        
    instrument = input("Enter Instrument (e.g., salamander-piano): ").strip().lower()
    tempo_bpm = int(input("Enter Tempo (BPM): ").strip())

    # 2. Initialize and Train AI
    print("\nInitializing and training AI model...")
    melody_engine = MelodyGenerator()
    training_data_path = Path(__file__).parent.parent / "training_data"
    melody_engine.train(str(training_data_path))

    # 3. Generate Musical Parts
    print(f"\nGenerating piece with progression: {custom_chord_list}...")
    
    # A. Create a chord stream from the user's list
    custom_chord_stream = create_stream_from_custom_progression(custom_chord_list)
    
    # B. Analyze the key to guide the melody
    try:
        analysis_key = custom_chord_stream.analyze('key')
        key_for_melody = analysis_key.tonic.name.upper() if analysis_key.mode == 'major' else analysis_key.tonic.name.lower()
    except Exception:
        key_for_melody = 'C' # Fallback
    
    # C. Generate the melody
    melody_stream = melody_engine.generate(length=len(custom_chord_list) * 4, key=key_for_melody)
    print("-> Musical parts generated.")

    # 4. Export using the NEW, dedicated exporter
    composition_name = f"Custom Test in {key_for_melody.capitalize()}"
    output_folder = Path(__file__).parent.parent / "output"
    
    _, xml_filepath = export_custom_composition(
        melody_stream=melody_stream,
        custom_chord_stream=custom_chord_stream,
        output_path=output_folder,
        composition_name=composition_name,
        instrument_name=instrument,
        bpm=tempo_bpm
    )
    
    # 5. Open the result
    if xml_filepath:
        print("\n--- Custom Progression Test Complete ---")
        open_in_musescore(xml_filepath)
    else:
        print("\n--- Custom Progression Test Failed ---")

if __name__ == "__main__":
    run_custom_test()