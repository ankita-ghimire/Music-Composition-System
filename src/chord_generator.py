# In src/chord_generator.py
# FINAL, VERIFIED, AND SYNTAX-CORRECTED VERSION

import copy
import random
from music21 import stream, chord, key

# ==============================================================================
# HELPER FUNCTIONS: To define the chord palettes
# ==============================================================================
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

# ==============================================================================
# ORIGINAL SOLO COMPOSER FUNCTION (Unchanged and Preserved)
# ==============================================================================
def generate_chords(key_root: str, mode: str, num_bars: int, mood: str = 'default') -> stream.Stream:
    """Generates a simple, repeating chord progression for the Solo Composer."""
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
        new_chord = copy.deepcopy(chords_dict[symbol])
        new_chord.duration.quarterLength = 4.0
        chord_stream.append(new_chord)

    return chord_stream

# ==============================================================================
# NEW ADVANCED ENSEMBLE FUNCTION (Syntax Corrected)
# ==============================================================================
def generate_structured_chords(key_root: str, mode: str, num_bars: int, mood: str = 'default') -> stream.Stream:
    """
    A NEW, advanced function that generates chord progressions using a song structure (Verse/Chorus).
    """
    print("Generating STRUCTURED chord progression...")
    
    final_mode = mode
    if mood == 'happy': final_mode = 'major'
    elif mood == 'sad': final_mode = 'minor'
    
    key_obj = key.Key(key_root, final_mode)

    # --- SYNTAX FIX IS HERE ---
    # The following block was incorrectly indented in your original code.
    if final_mode == 'major':
        chords_dict = get_major_triads(key_obj)
    else: # minor
        chords_dict = get_minor_triads(key_obj)
    # --- END OF FIX ---

    # Define different progressions for different sections
    if final_mode == 'major':
        verse_prog = ["I", "vi", "IV", "V"]
        chorus_prog = ["IV", "I", "V", "vi"]
    else: # minor
        verse_prog = ["i", "VI", "iv", "v"]
        chorus_prog = ["iv", "v", "i", "VI"]

    chord_stream = stream.Stream()
    
    # Simple song structure: 4 bars of Verse, 4 bars of Chorus, repeat
    for i in range(num_bars):
        section_index = i % 4
        if (i // 4) % 2 == 0: # Verse sections
            current_prog = verse_prog
        else: # Chorus sections
            current_prog = chorus_prog
            
        symbol = current_prog[section_index]
        new_chord = copy.deepcopy(chords_dict[symbol])
        new_chord.duration.quarterLength = 4.0
        chord_stream.append(new_chord)
        
    return chord_stream