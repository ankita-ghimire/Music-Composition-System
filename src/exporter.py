# In src/exporter.py
# FINAL, COMPLETE, AND UNIFIED VERSION
# This file contains three separate, dedicated export functions for each feature.

from pathlib import Path
from music21 import stream, clef, metadata, meter, instrument, tempo

# ==============================================================================
# FEATURE 1: SOLO COMPOSER EXPORTER
# ==============================================================================
def export_solo_composition(melody_stream, chord_stream, output_path: Path, 
                            composition_name: str, instrument_name: str, bpm: int):
    """
    Exports a SOLO piece, intelligently combining melody and chords onto a single
    Grand Staff for a single instrument (typically Piano).
    """
    print("Assembling SOLO score for export...")
    try:
        # --- Create the main Score object with metadata ---
        full_score = stream.Score()
        full_score.insert(0, metadata.Metadata(title=composition_name, composer="Generative AI System"))
        full_score.insert(0, tempo.MetronomeMark(number=bpm))
        
        # --- Create a single Piano Part (Grand Staff) ---
        # This part will hold both the melody and the chords.
        main_part = stream.Part(id='main_instrument')
        
        # Assign the user's chosen instrument
        if instrument_name == 'flute': main_part.insert(0, instrument.Flute())
        elif instrument_name == 'violin': main_part.insert(0, instrument.Violin())
        else: main_part.insert(0, instrument.Piano())

        # --- THE CRITICAL FIX FOR MEASURES ---
        # A Part needs a time signature BEFORE you can make measures from it.
        main_part.insert(0, meter.TimeSignature('4/4'))

        # Add all melody and chord notes to this single part.
        # music21 will automatically distribute them between treble and bass clefs.
        for element in melody_stream.flatten().notesAndRests:
            main_part.append(element)
        for element in chord_stream.flatten().notesAndRests:
            main_part.append(element)
        
        # Now that the part is full, create the measures.
        main_part.makeMeasures(inPlace=True)
        
        # Insert the completed, measured part into the main score
        full_score.insert(0, main_part)
        
        print("-> Solo score assembled and measures calculated.")
        
        # --- File Export Logic ---
        safe_filename = "".join(c for c in composition_name if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')
        output_path.mkdir(exist_ok=True)
        out_midi = output_path / f"{safe_filename}.mid"
        out_xml = output_path / f"{safe_filename}.mxl"
        
        full_score.write("midi", fp=str(out_midi))
        full_score.write("musicxml", fp=str(out_xml))
        
        print(f"✅ Solo composition exported successfully!")
        return str(out_midi), str(out_xml)

    except Exception as e:
        import traceback; traceback.print_exc(); return None, None


# ==============================================================================
# FEATURE 2: ENSEMBLE ARRANGER EXPORTER
# ==============================================================================
def export_ensemble_composition(melody_stream, accomp_stream, output_path: Path, 
                                  composition_name: str, lead_instrument_name: str, 
                                  accomp_instrument_name: str, bpm: int):
    """
    A SEPARATE function specifically for exporting multi-part ENSEMBLE scores.
    """
    print("Assembling ENSEMBLE score for export...")
    try:
        # --- Instrument Assignment ---
        if lead_instrument_name == 'flute': lead_inst = instrument.Flute()
        elif lead_instrument_name == 'violin': lead_inst = instrument.Violin()
        else: lead_inst = instrument.Piano()
        
        if accomp_instrument_name == 'guitar-acoustic': accomp_inst = instrument.AcousticGuitar()
        else: accomp_inst = instrument.Piano()

        # --- Create a separate Part for each instrument ---
        melody_part = stream.Part(id='melody')
        melody_part.insert(0, lead_inst)
        melody_part.insert(0, meter.TimeSignature('4/4'))
        for n in melody_stream.flatten().notesAndRests: melody_part.append(n)
        melody_part.makeMeasures(inPlace=True)

        accomp_part = stream.Part(id='accompaniment')
        accomp_part.insert(0, accomp_inst)
        accomp_part.insert(0, meter.TimeSignature('4/4'))
        for n in accomp_stream.flatten().notesAndRests: accomp_part.append(n)
        accomp_part.makeMeasures(inPlace=True)
        
        # --- Assemble Final Score ---
        full_score = stream.Score()
        full_score.insert(0, metadata.Metadata(title=composition_name, composer="AI Ensemble"))
        full_score.insert(0, tempo.MetronomeMark(number=bpm))
        full_score.insert(0, melody_part)
        full_score.insert(0, accomp_part)
        
        print("-> Ensemble score assembled and measures calculated.")
        
        # --- File Export Logic ---
        safe_filename = "".join(c for c in composition_name if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')
        output_path.mkdir(exist_ok=True)
        out_midi = output_path / f"{safe_filename}.mid"
        out_xml = output_path / f"{safe_filename}.mxl"
        full_score.write("midi", fp=str(out_midi))
        full_score.write("musicxml", fp=str(out_xml))
        
        print(f"✅ Ensemble composition exported successfully!")
        return str(out_midi), str(out_xml)

    except Exception as e:
        import traceback; traceback.print_exc(); return None, None


# ==============================================================================
# FEATURE 3: CHORD CLUSTER EXPORTER
# ==============================================================================

# In src/exporter.py

# --- ADD THIS NEW FUNCTION AT THE END OF THE FILE ---

def export_custom_composition(melody_stream, custom_chord_stream, output_path, 
                              composition_name, instrument_name, bpm):
    """
    A NEW function for exporting a single-instrument piece with a custom
    user-defined chord progression. This version has the definitive fix for the 'no measures' error.
    """
    from music21 import stream, metadata, tempo, instrument, meter # Add meter to local imports
    
    print("Assembling CUSTOM PROGRESSION score for export...")
    try:
        # --- Create the main Score object with metadata ---
        full_score = stream.Score()
        full_score.insert(0, metadata.Metadata(title=composition_name, composer="Generative AI System"))
        full_score.insert(0, tempo.MetronomeMark(number=bpm))
        
        # --- Create and Structure the Instrument Part ---
        main_part = stream.Part(id='main_instrument')
        
        # Assign the user's chosen instrument
        if instrument_name == 'flute': main_part.insert(0, instrument.Flute())
        elif instrument_name == 'violin': main_part.insert(0, instrument.Violin())
        else: main_part.insert(0, instrument.Piano())

        # --- THE DEFINITIVE FIX IS HERE ---
        # A Part needs a time signature BEFORE you can make measures from it.
        main_part.insert(0, meter.TimeSignature('4/4'))
        # --- END OF FIX ---

        # Add BOTH the melody and the custom chords to this single part.
        for element in melody_stream.flatten().notesAndRests:
            main_part.append(element)
        for element in custom_chord_stream.flatten().notesAndRests:
            main_part.append(element)
        
        # Now that the part is complete with a time signature, create the measures.
        main_part.makeMeasures(inPlace=True)
        
        # Insert the completed, measured part into the main score
        full_score.insert(0, main_part)
        
        print("-> Custom score assembled and measures calculated.")
        
        # --- File Export Logic ---
        safe_filename = "".join(c for c in composition_name if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')
        output_path.mkdir(exist_ok=True)
        out_midi = output_path / f"{safe_filename}.mid"
        out_xml = output_path / f"{safe_filename}.mxl"
        
        full_score.write("midi", fp=str(out_midi))
        full_score.write("musicxml", fp=str(out_xml))
        
        return str(out_midi), str(out_xml)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, None