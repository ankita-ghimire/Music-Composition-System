from music21 import stream, note
import os

# Create a simple scale
melody = stream.Stream()
for pitch in ["C4", "D4", "E4", "F4", "G4"]:
    melody.append(note.Note(pitch, quarterLength=1))

# Ensure output directory exists
os.makedirs('../output', exist_ok=True)

# Save to MIDI
melody.write("midi", fp="../output/test_scale.mid")
print("✅ MIDI file created at output/test_scale.mid")
