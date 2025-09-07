# In src/chord_generator.py
# FINAL, COMPLETE, AND BUG-FIXED VERSION
import copy # <-- IMPORT THE COPY LIBRARY
from music21 import stream, chord, key

def get_major_triads(scale_obj):
    """Builds major chords by getting each pitch individually from the scale."""
    return {
        "I": chord.Chord([scale_obj.pitchFromDegree(1), scale_obj.pitchFromDegree(3), scale_obj.pitchFromDegree(5)]),
        "IV": chord.Chord([scale_obj.pitchFromDegree(4), scale_obj.pitchFromDegree(6), scale_obj.pitchFromDegree(1).transpose('P8')]),
        "V": chord.Chord([scale_obj.pitchFromDegree(5), scale_obj.pitchFromDegree(7), scale_obj.pitchFromDegree(2).transpose('P8')]),
        "vi": chord.Chord([scale_obj.pitchFromDegree(6), scale_obj.pitchFromDegree(1).transpose('P8'), scale_obj.pitchFromDegree(3).transpose('P8')])
    }

def get_minor_triads(scale_obj):
    """Builds minor chords by getting each pitch individually from the scale."""
    return {
        "i": chord.Chord([scale_obj.pitchFromDegree(1), scale_obj.pitchFromDegree(3), scale_obj.pitchFromDegree(5)]),
        "iv": chord.Chord([scale_obj.pitchFromDegree(4), scale_obj.pitchFromDegree(6), scale_obj.pitchFromDegree(1).transpose('P8')]),
        "v": chord.Chord([scale_obj.pitchFromDegree(5), scale_obj.pitchFromDegree(7), scale_obj.pitchFromDegree(2).transpose('P8')]),
        "VI": chord.Chord([scale_obj.pitchFromDegree(6), scale_obj.pitchFromDegree(1).transpose('P8'), scale_obj.pitchFromDegree(3).transpose('P8')])
    }

def generate_chords(key_root: str, mode: str, num_bars: int, mood: str = 'default') -> stream.Stream:
    """Generates a chord progression as a music21 Stream object."""
    final_mode = mode
    if mood == 'happy': final_mode = 'major'
    elif mood == 'sad': final_mode = 'minor'
    
    k = key.Key(key_root, final_mode)
    
    if final_mode == 'major':
        chords_dict = get_major_triads(k)
        template = ["I", "V", "vi", "IV"]
    else: # minor
        chords_dict = get_minor_triads(k)
        template = ["i", "VI", "iv", "v"]

    chord_stream = stream.Stream()
    for i in range(num_bars):
        symbol = template[i % len(template)]
        
        # --- THE CRITICAL FIX ---
        # Instead of referencing the original chord, we create a deep copy of it.
        # This gives us a brand new object with a new memory ID for each bar.
        new_chord = copy.deepcopy(chords_dict[symbol])
        # --- END FIX ---

        new_chord.duration.quarterLength = 4.0
        chord_stream.append(new_chord)

    return chord_stream