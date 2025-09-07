# In src/chord_generator.py
# FINAL, BRUTALLY SIMPLE, AND VERIFIED VERSION

import random
import copy
from music21 import stream, chord, key, interval

def generate_chords(key_root: str, mode: str, num_bars: int, mood: str = 'default', is_structured=False) -> stream.Stream:
    """
    This is the single, unified chord generator. It produces standard, reliable
    chord.Chord objects to guarantee compatibility with the arranger.
    """
    # 1. Determine the final mode based on mood
    final_mode = mode
    if mood == 'happy': final_mode = 'major'
    elif mood == 'sad': final_mode = 'minor'

    # 2. Define the chord progressions in a base key (C Major / A minor)
    #    This is the most reliable way to create standard Chord objects.
    if final_mode == 'major':
        verse_base = [chord.Chord("C E G"), chord.Chord("G B D"), chord.Chord("A C E"), chord.Chord("F A C")]
        chorus_base = [chord.Chord("F A C"), chord.Chord("C E G"), chord.Chord("G B D"), chord.Chord("A C E")]
        simple_base = verse_base
        source_key_tonic = 'C'
    else: # minor
        verse_base = [chord.Chord("A C E"), chord.Chord("F A C"), chord.Chord("D F A"), chord.Chord("E G B")]
        chorus_base = [chord.Chord("D F A"), chord.Chord("E G B"), chord.Chord("A C E"), chord.Chord("F A C")]
        simple_base = verse_base
        source_key_tonic = 'a'

    # 3. Transpose these reliable chords to the user's desired key
    target_key = key.Key(key_root, final_mode)
    transposition_interval = interval.Interval(key.Key(source_key_tonic).tonic, target_key.tonic)
    
    verse_prog = [c.transpose(transposition_interval) for c in verse_base]
    chorus_prog = [c.transpose(transposition_interval) for c in chorus_base]
    simple_prog = [c.transpose(transposition_interval) for c in simple_base]

    # 4. Build the final stream
    chord_stream = stream.Stream()
    
    for i in range(num_bars):
        section_index = i % 4
        
        # Use the structured progression if requested, otherwise the simple one
        if is_structured:
            if (i // 4) % 2 == 0: current_prog = verse_prog
            else: current_prog = chorus_prog
        else:
            current_prog = simple_prog
            
        new_chord = copy.deepcopy(current_prog[section_index])
        new_chord.duration.quarterLength = 4.0
        chord_stream.append(new_chord)
        
    return chord_stream

