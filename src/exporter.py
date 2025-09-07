# In src/exporter.py
# FINAL, BULLETPROOF VERSION (8)
from pathlib import Path
from music21 import stream, clef, metadata, meter, instrument, tempo

def export_composition(melody_stream, chord_stream, output_path: Path, composition_name: str, 
                       instrument_name='salamander-piano', bpm=120):
    """
    (FINAL, BULLETPROOF VERSION)
    This version builds the score directly to prevent the 'no measures' error.
    """
    try:
        print("Assembling final score for export...")

        # --- Create a single Score object to hold everything ---
        full_score = stream.Score()
        
        # --- Create and configure the Melody Part ---
        melody_part = stream.Part(id='melody')
        melody_part.append(clef.TrebleClef())
        
        # Assign the correct instrument
        if instrument_name == 'flute': melody_part.insert(0, instrument.Flute())
        elif instrument_name == 'violin': melody_part.insert(0, instrument.Violin())
        else: melody_part.insert(0, instrument.Piano())
        
        # Add all the notes from the generated melody stream
        for n in melody_stream.flatten().notesAndRests:
            melody_part.append(n)

        # --- Create and configure the Chord Part ---
        chord_part = stream.Part(id='chords')
        chord_part.append(clef.BassClef())
        chord_part.insert(0, instrument.Piano()) # Chords are always piano
        
        # Add all the chords from the generated chord stream
        for c in chord_stream.flatten().notesAndRests:
            chord_part.append(c)

        # --- Insert Parts and Metadata into the Score ---
        full_score.insert(0, metadata.Metadata(title=composition_name, composer="Generative AI System"))
        full_score.insert(0, tempo.MetronomeMark(number=bpm))
        full_score.insert(0, melody_part)
        full_score.insert(0, chord_part)
        
        # --- THE DEFINITIVE FIX ---
        # By calling .makeNotation(), we force music21 to process everything,
        # including creating measures, before we attempt to write the file.
        # This is the most robust way to ensure the score is valid.
        full_score.makeNotation(inPlace=True)
        
        print("-> Score assembled and notation created.")

        # --- Export Files ---
        safe_filename = "".join(c for c in composition_name if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')
        output_path.mkdir(exist_ok=True)
        out_midi = output_path / f"{safe_filename}.mid"
        out_xml = output_path / f"{safe_filename}.mxl"

        full_score.write("midi", fp=str(out_midi))
        full_score.write("musicxml", fp=str(out_xml))
        
        print(f"✅ Composition exported successfully!")
        return str(out_midi), str(out_xml)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, None