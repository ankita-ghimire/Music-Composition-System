"""
Chord Generator Module
----------------------
Generates chord progressions for a given key and mode.
Also provides helper to open outputs directly in MuseScore.
"""

import os, platform, subprocess
from pathlib import Path
from music21 import stream, chord, key, tempo
import copy

# -------------------------------
# Helper to open outputs
# -------------------------------
def open_outputs(midi_path: str, xml_path: str):
    """
    Open both MIDI + MusicXML directly in MuseScore (no VLC).
    """
    midi_path = str(Path(midi_path).resolve())
    xml_path = str(Path(xml_path).resolve())
    system = platform.system()

    try:
        if system == "Windows":
            possible_paths = [
                r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe",
                r"C:\Program Files\MuseScore 3\bin\MuseScore3.exe"
            ]
            for ms_path in possible_paths:
                if os.path.exists(ms_path):
                    # Open both files in MuseScore
                    subprocess.Popen([ms_path, midi_path])
                    subprocess.Popen([ms_path, xml_path])
                    print(f"Opened in MuseScore: {xml_path} and {midi_path}")
                    return
            print("MuseScore not found in default path. Please open the files manually.")
        elif system == "Darwin":  # macOS
            subprocess.run(["open", "-a", "MuseScore", midi_path])
            subprocess.run(["open", "-a", "MuseScore", xml_path])
            print(f"Opened in MuseScore: {xml_path} and {midi_path}")
        else:  # Linux
            subprocess.run(["musescore", midi_path])
            subprocess.run(["musescore", xml_path])
            print(f"Opened in MuseScore: {xml_path} and {midi_path}")
    except Exception as e:
        print(f"Could not open in MuseScore automatically: {e}")

# -------------------------------
# Chord triads
# -------------------------------
def get_major_triads(scale_obj):
    return {
        "I": chord.Chord([scale_obj.pitchFromDegree(1),
                          scale_obj.pitchFromDegree(3),
                          scale_obj.pitchFromDegree(5)]),
        "IV": chord.Chord([scale_obj.pitchFromDegree(4),
                           scale_obj.pitchFromDegree(6),
                           scale_obj.pitchFromDegree(1)]),
        "V": chord.Chord([scale_obj.pitchFromDegree(5),
                          scale_obj.pitchFromDegree(7),
                          scale_obj.pitchFromDegree(2)]),
        "vi": chord.Chord([scale_obj.pitchFromDegree(6),
                           scale_obj.pitchFromDegree(1),
                           scale_obj.pitchFromDegree(3)])
    }

def get_minor_triads(scale_obj):
    return {
        "i": chord.Chord([scale_obj.pitchFromDegree(1),
                          scale_obj.pitchFromDegree(3),
                          scale_obj.pitchFromDegree(5)]),
        "iv": chord.Chord([scale_obj.pitchFromDegree(4),
                           scale_obj.pitchFromDegree(6),
                           scale_obj.pitchFromDegree(1)]),
        "v": chord.Chord([scale_obj.pitchFromDegree(5),
                          scale_obj.pitchFromDegree(7),
                          scale_obj.pitchFromDegree(2)]),
        "VI": chord.Chord([scale_obj.pitchFromDegree(6),
                           scale_obj.pitchFromDegree(1),
                           scale_obj.pitchFromDegree(3)])
    }

# -------------------------------
# Chord progression generator
# -------------------------------
def generate_chords(key_name="C", mode="major", num_bars=4):
    k = key.Key(key_name, mode)

    if mode.lower() == "major":
        chords_dict = get_major_triads(k)
        templates = [["I", "vi", "IV", "V"], ["I", "IV", "V", "I"]]
    else:
        chords_dict = get_minor_triads(k)
        templates = [["i", "VI", "iv", "V"], ["i", "iv", "V", "i"]]

    template = templates[0]
    chord_stream = stream.Stream()
    chord_stream.append(tempo.MetronomeMark(number=100))

    for i in range(num_bars):
        symbol = template[i % len(template)]
        if symbol in chords_dict:
            c = copy.deepcopy(chords_dict[symbol])
            c.lyric = symbol
            c.quarterLength = 4.0
            chord_stream.append(c)
        else:
            tonic = copy.deepcopy(list(chords_dict.values())[0])
            tonic.quarterLength = 4.0
            chord_stream.append(tonic)

    return chord_stream
