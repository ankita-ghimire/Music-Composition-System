# In src/arranger.py
from music21 import stream, note

def create_arpeggiated_accompaniment(chord_stream: stream.Stream) -> stream.Part:
    """
    Takes a stream of chords and creates a simple arpeggiated accompaniment Part.
    This is the "brain" of the ensemble's harmony player.
    """
    accomp_part = stream.Part()
    arpeggio_pattern = [0, 1, 2, 1] # Root, Third, Fifth, Third

    for ch in chord_stream.getElementsByClass('Chord'):
        pitches = ch.pitches
        if len(pitches) < 3: continue

        for pattern_index in arpeggio_pattern:
            new_note = note.Note(pitches[pattern_index])
            new_note.quarterLength = 0.5 # Eighth note
            accomp_part.append(new_note)
            
    return accomp_part