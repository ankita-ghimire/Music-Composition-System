
import random
import copy
from music21 import stream, chord, key, interval

def generate_chords(key_root: str, mode: str, num_bars: int, mood: str = 'default', is_structured=False) -> stream.Stream:
    
    final_mode = mode
    if mood == 'happy': final_mode = 'major'
    elif mood == 'sad': final_mode = 'minor'

    if final_mode == 'major':
        verse_base = [chord.Chord("C E G"), chord.Chord("G B D"), chord.Chord("A C E"), chord.Chord("F A C")]
        chorus_base = [chord.Chord("F A C"), chord.Chord("C E G"), chord.Chord("G B D"), chord.Chord("A C E")]
        simple_base = verse_base
        source_key_tonic = 'C'
    else: 
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
        
        if is_structured:
            if (i // 4) % 2 == 0: current_prog = verse_prog
            else: current_prog = chorus_prog
        else:
            current_prog = simple_prog
            
        new_chord = copy.deepcopy(current_prog[section_index])
        new_chord.duration.quarterLength = 4.0
        chord_stream.append(new_chord)
        
    return chord_stream

def create_stream_from_custom_progression(chord_names: list) -> stream.Stream:
    
    from music21 import stream, chord # Local import
    
    custom_chord_stream = stream.Stream()
    for name in chord_names:
        try:
            new_chord = chord.Chord(name)
            new_chord.duration.quarterLength = 4.0
            custom_chord_stream.append(new_chord)
        except Exception:
            print(f"Warning: Could not parse chord name '{name}'.")
    return custom_chord_stream