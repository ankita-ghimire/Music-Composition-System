# src/utils.py
import os, platform, subprocess
from pathlib import Path
from mido import MidiFile, MidiTrack, Message

# -------------------------------
# Save melody (list of notes) to MIDI
# -------------------------------
def save_melody_to_midi(melody_events, filename):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    NOTE_DURATION_TICKS = 240
    for note, pause in melody_events:
        track.append(Message('note_on', note=int(note), velocity=64, time=int(pause)))
        track.append(Message('note_off', note=int(note), velocity=64, time=NOTE_DURATION_TICKS))

    mid.save(filename)

# -------------------------------
# Combine melody + chords into one MIDI
# -------------------------------
def combine_chords_and_melody(chords_stream, melody_events, filename):
    chords_stream.write("midi", fp=filename.replace(".mid", "_chords.mid"))
    save_melody_to_midi(melody_events, filename.replace(".mid", "_melody.mid"))
    # (Later you can merge tracks if you want them in one file)

# -------------------------------
# Try to open file in MuseScore
# -------------------------------
def open_with_musescore(path: str):
    path = str(Path(path).resolve())
    system = platform.system()

    if system == "Windows":
        possible_paths = [
            r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe",
            r"C:\Program Files\MuseScore 3\bin\MuseScore3.exe"
        ]
        for ms_path in possible_paths:
            if os.path.exists(ms_path):
                subprocess.Popen([ms_path, path])
                return
        os.startfile(path)

    elif system == "Darwin":  # Mac
        try:
            subprocess.run(["open", "-a", "MuseScore", path])
        except:
            subprocess.run(["open", path])

    else:  # Linux
        try:
            subprocess.run(["musescore", path])
        except:
            subprocess.run(["xdg-open", path])
