"""
Main Music Composition System
------------------------------
Integrates melody + chord generation.
Exports both MIDI (for playback) and MusicXML (for notation).
"""

from pathlib import Path
import time
from music21 import stream
from melody_generator import MelodyGenerator
from chord_generator import generate_chords, open_outputs

def main():
    print("=== Music Composition System ===\n")

    # 1) User input
    key_name = input("Enter key (C, D, E, F, G, A, B): ").strip().upper()
    mode = input("Enter mode (major/minor): ").strip().lower()
    num_bars_input = input("Enter number of bars (default 4): ").strip()

    try:
        num_bars = int(num_bars_input)
        if num_bars <= 0:
            raise ValueError
    except:
        num_bars = 4
        print("Invalid number of bars! Defaulting to 4.")

    print(f"\nGenerating composition in {key_name} {mode}, {num_bars} bars...")

    # 2) Create melody engine and TRAIN it
    melody_engine = MelodyGenerator()

    # Adjust this path if your training_data folder is located differently
    training_data_path = Path(__file__).parent.parent / "training_data"

    if training_data_path.exists():
        melody_engine.train(str(training_data_path))
    else:
        print(f"⚠ Training data folder not found at {training_data_path}. Using fallback melodies.")

    # 3) Generate melody (4 notes per bar → num_bars*4 notes)
    melody = melody_engine.generate(num_bars, key=key_name, mode=mode)

    # 4) Generate chords
    chords = generate_chords(key_name, mode, num_bars)

    # 5) Combine melody + chords
    composition = stream.Stream()
    composition.insert(0, chords)
    composition.insert(0, melody)

    # 6) Export files
    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)

    out_midi = out_dir / "composed_song.mid"
    out_xml = out_dir / "composed_song.mxl"

    composition.write("midi", fp=str(out_midi))
    composition.write("musicxml", fp=str(out_xml))

    print(f"\n Exported MIDI: {out_midi}")
    print(f"Exported MusicXML: {out_xml}")

    # 7) Wait a second before opening
    time.sleep(1)

    # 8) Auto-open only with MuseScore
    open_outputs(out_midi, out_xml)

if __name__ == "__main__":
    main()
