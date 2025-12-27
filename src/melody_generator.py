import random
import os
from mido import MidiFile
from music21 import stream, note, scale

class MelodyGenerator:
    
    def __init__(self):
        self.chain = {}

    def train(self, midi_folder_path):
        all_events = []
        if not os.path.exists(midi_folder_path): return
        for filename in os.listdir(midi_folder_path):
            if filename.lower().endswith(('.mid', '.midi')):
                file_path = os.path.join(midi_folder_path, filename)
                events = self._get_musical_events_from_midi(file_path)
                all_events.extend(events)
        if not all_events: return

        print("Building Markov Chain...")
        chain = {}
        for i in range(len(all_events) - 1):
            current_event = all_events[i]
            next_event = all_events[i+1]
            
            if current_event not in chain:
                chain[current_event] = []
            
            chain[current_event].append(next_event)
            
        self.chain = chain

    def generate(self, length: int, key: str = 'C', temperature: float = 1.0, mood: str = 'default') -> stream.Part:
        
        melody_stream = stream.Part()
        if not self.chain: return melody_stream
        
        note_duration = 0.5
        if mood == 'sad' or mood == 'calm': note_duration = 1.0
        elif mood == 'energetic': note_duration = 0.25
        
        mode = 'major' if key.isupper() else 'minor'
        key_scale = scale.MajorScale(key) if mode == "major" else scale.MinorScale(key)
        scale_notes = [p.midi for p in key_scale.getPitches()]

        try: current_event = random.choice(list(self.chain.keys()))
        except IndexError: return melody_stream

        for _ in range(length):
            pitch = current_event[0]
            if pitch not in scale_notes: pitch = random.choice(scale_notes)
            new_note = note.Note(pitch)
            new_note.quarterLength = note_duration
            melody_stream.append(new_note)
            possible_next = self.chain.get(current_event, [])
            current_event = random.choice(possible_next if possible_next else list(self.chain.keys()))
        return melody_stream

    def _get_musical_events_from_midi(self, file_path):
        events = []
        try:
            midi = MidiFile(file_path)
            for msg in midi:
                if msg.type == 'note_on' and msg.velocity > 0:
                    events.append((msg.note, msg.time))
        except Exception: pass
        return events

    
    def generate_creative_melody(self, length: int, key: str = 'C', temperature: float = 1.0, mood: str = 'default') -> stream.Part:
        
        print("Generating CREATIVE melody with temperature...")
        melody_stream = stream.Part()
        if not self.chain: return melody_stream
        
        # Mood logic for rhythm
        note_duration = 0.5
        if mood == 'sad': note_duration = 1.0
        elif mood == 'energetic': note_duration = 0.25
        
        mode = 'major' if key.isupper() else 'minor'
        key_scale = scale.MajorScale(key) if mode == "major" else scale.MinorScale(key)
        
        scale_notes = [p.midi for p in key_scale.getPitches()]
        
        try:
            current_event = random.choice(list(self.chain.keys()))
        except IndexError:
            return melody_stream

        for _ in range(length):
            pitch = current_event[0]
            if pitch not in scale_notes:
                pitch = random.choice(scale_notes)
            
            new_note = note.Note(pitch)
            new_note.quarterLength = note_duration
            melody_stream.append(new_note)

            possible_next = self.chain.get(current_event, [])
            if not possible_next:
                current_event = random.choice(list(self.chain.keys()))
            else:
                # Temperature-Aware Choice Logic
                if temperature < 0.5:
                    next_event = max(set(possible_next), key=possible_next.count)
                else:
                    next_event = random.choice(possible_next)
                current_event = next_event
        
        return melody_stream
