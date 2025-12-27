
from pathlib import Path
from music21 import stream, clef, metadata, meter, instrument, tempo

def export_solo_composition(melody_stream, chord_stream, output_path: Path, 
                            composition_name: str, instrument_name: str, bpm: int):
    
    print("Assembling SOLO score for export...")
    try:
        
        full_score = stream.Score()
        full_score.insert(0, metadata.Metadata(title=composition_name, composer="Generative AI System"))
        full_score.insert(0, tempo.MetronomeMark(number=bpm))
       
        main_part = stream.Part(id='main_instrument')
        
        
        if instrument_name == 'flute': main_part.insert(0, instrument.Flute())
        elif instrument_name == 'violin': main_part.insert(0, instrument.Violin())
        else: main_part.insert(0, instrument.Piano())

        main_part.insert(0, meter.TimeSignature('4/4'))
        for element in melody_stream.flatten().notesAndRests:
            main_part.append(element)
        for element in chord_stream.flatten().notesAndRests:
            main_part.append(element)
        main_part.makeMeasures(inPlace=True)
        full_score.insert(0, main_part)
        
        print("-> Solo score assembled and measures calculated.")
        
        safe_filename = "".join(c for c in composition_name if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')
        output_path.mkdir(exist_ok=True)
        out_midi = output_path / f"{safe_filename}.mid"
        out_xml = output_path / f"{safe_filename}.xml"
        
        full_score.write("midi", fp=str(out_midi))
        full_score.write("musicxml", fp=str(out_xml))
        
        print(f"Solo composition exported successfully!")
        return str(out_midi), str(out_xml)

    except Exception as e:
        import traceback; traceback.print_exc(); return None, None

def export_ensemble_composition(melody_stream, accomp_stream, output_path: Path, 
                                  composition_name: str, lead_instrument_name: str, 
                                  accomp_instrument_name: str, bpm: int):
    
    print("Assembling ENSEMBLE score for export...")
    try:
       
        if lead_instrument_name == 'flute': lead_inst = instrument.Flute()
        elif lead_instrument_name == 'violin': lead_inst = instrument.Violin()
        else: lead_inst = instrument.Piano()
        
        if accomp_instrument_name == 'guitar-acoustic': accomp_inst = instrument.AcousticGuitar()
        else: accomp_inst = instrument.Piano()

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
        
        full_score = stream.Score()
        full_score.insert(0, metadata.Metadata(title=composition_name, composer="AI Ensemble"))
        full_score.insert(0, tempo.MetronomeMark(number=bpm))
        full_score.insert(0, melody_part)
        full_score.insert(0, accomp_part)
        
        print("-> Ensemble score assembled and measures calculated.")
        
        safe_filename = "".join(c for c in composition_name if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')
        output_path.mkdir(exist_ok=True)
        out_midi = output_path / f"{safe_filename}.mid"
        out_xml = output_path / f"{safe_filename}.xml"
        full_score.write("midi", fp=str(out_midi))
        full_score.write("musicxml", fp=str(out_xml))
        
        print(f"Ensemble composition exported successfully!")
        return str(out_midi), str(out_xml)

    except Exception as e:
        import traceback; traceback.print_exc(); return None, None

def export_custom_composition(melody_stream, custom_chord_stream, output_path, 
                              composition_name, instrument_name, bpm):
    
    from music21 import stream, metadata, tempo, instrument, meter # Add meter to local imports
    
    print("Assembling CUSTOM PROGRESSION score for export...")
    try:
       
        full_score = stream.Score()
        full_score.insert(0, metadata.Metadata(title=composition_name, composer="Generative AI System"))
        full_score.insert(0, tempo.MetronomeMark(number=bpm))
        
        main_part = stream.Part(id='main_instrument')
        if instrument_name == 'flute': main_part.insert(0, instrument.Flute())
        elif instrument_name == 'violin': main_part.insert(0, instrument.Violin())
        else: main_part.insert(0, instrument.Piano())

        main_part.insert(0, meter.TimeSignature('4/4'))
        
        for element in melody_stream.flatten().notesAndRests:
            main_part.append(element)
        for element in custom_chord_stream.flatten().notesAndRests:
            main_part.append(element)
        main_part.makeMeasures(inPlace=True)
       
        full_score.insert(0, main_part)
        
        print("-> Custom score assembled and measures calculated.")
        safe_filename = "".join(c for c in composition_name if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')
        output_path.mkdir(exist_ok=True)
        out_midi = output_path / f"{safe_filename}.mid"
        out_xml = output_path / f"{safe_filename}.xml"
        
        full_score.write("midi", fp=str(out_midi))
        full_score.write("musicxml", fp=str(out_xml))
        return str(out_midi), str(out_xml)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, None