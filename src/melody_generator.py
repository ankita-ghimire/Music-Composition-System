import random
import os
from mido import MidiFile
from music21 import stream, note, scale

class MelodyGenerator:
    """
    A class to generate melodies using a Markov chain, trained on MIDI files.
    Returns music21 streams so it integrates directly with chords.
    """
    def __init__(self):
        self.chain = {}
        self.trained_notes = []

    # -------------------------------
    # Training
    # -------------------------------
    def train(self, midi_folder_path):
        """Train the Markov model on all MIDI files in a given folder."""
        all_events = []
        print("Starting training...")
        for filename in os.listdir(midi_folder_path):
            if filename.lower().endswith(('.mid', '.midi')):
                file_path = os.path.join(midi_folder_path, filename)
                print(f"  - Processing {filename}")
                events_from_song = self._get_musical_events_from_midi(file_path)
                all_events.extend(events_from_song)
        
        self.trained_notes = [e[0] for e in all_events]
        self.chain = self._build_markov_chain(all_events)
        print(f"\nTraining complete. Model built from {len(all_events)} events.")

    # -------------------------------
    # Melody generation
    # -------------------------------
    def generate(self, num_bars=4, key='C', mode='major', start_note=None):
        """
        Generates a melody aligned to bars.
        Returns: music21.stream.Part
        """
        melody = stream.Part()

        # Fallback if not trained
        if not self.chain:
            print("⚠ No training data found. Falling back to scale-based melody.")
            return self._fallback_scale_melody(num_bars, key, mode)

        # Choose scale
        key_scale = scale.MajorScale(key) if mode == "major" else scale.MinorScale(key)
        scale_notes = [p.midi for p in key_scale.getPitches()]

        # Pick starting event
        if start_note and start_note in self.trained_notes:
            possible_starts = [event for event in self.chain.keys() if event[0] == start_note]
            current_event = random.choice(possible_starts) if possible_starts else random.choice(list(self.chain.keys()))
        else:
            current_event = random.choice(list(self.chain.keys()))

        # Generate melody notes (4 notes per bar → num_bars*4 total)
        for _ in range(num_bars * 4):
            pitch = current_event[0]

            # Keep notes inside the scale most of the time
            if pitch not in scale_notes:
                pitch = random.choice(scale_notes)

            n = note.Note(pitch)
            n.quarterLength = 1.0
            melody.append(n)

            # Move to next event
            possible_next = self.chain.get(current_event, [])
            if possible_next:
                current_event = random.choice(possible_next)
            else:
                current_event = random.choice(list(self.chain.keys()))

        return melody

    # -------------------------------
    # Private helpers
    # -------------------------------
    def _get_musical_events_from_midi(self, file_path):
        """Extracts (note, time) tuples from a MIDI file."""
        events = []
        try:
            midi_file = MidiFile(file_path)
            for track in midi_file.tracks:
                for msg in track:
                    if msg.type == 'note_on' and msg.velocity > 0:
                        event = (msg.note, msg.time)
                        events.append(event)
        except Exception as e:
            print(f"Could not read file {file_path}: {e}")
        return events

    def _build_markov_chain(self, events):
        """Builds the transition model from a list of events."""
        chain = {}
        for i in range(len(events) - 1):
            current_event = events[i]
            next_event = events[i+1]
            if current_event not in chain:
                chain[current_event] = []
            chain[current_event].append(next_event)
        return chain

    def _fallback_scale_melody(self, num_bars, key, mode):
        """Fallback if training data is missing → simple scale melody."""
        melody = stream.Part()
        key_scale = scale.MajorScale(key) if mode == "major" else scale.MinorScale(key)
        scale_notes = [p.midi for p in key_scale.getPitches()]

        for _ in range(num_bars * 4):
            pitch = random.choice(scale_notes)
            n = note.Note(pitch)
            n.quarterLength = 1.0
            melody.append(n)
        return melody
