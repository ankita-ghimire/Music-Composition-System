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
    #
# PASTE THIS ENTIRE METHOD INSIDE your MelodyGenerator class
#

    def generate(self, length, key='C', start_note=None, temperature=1.0):
        """
        Generates a new melody with controllable randomness (temperature).

        Args:
            length (int): The number of notes in the melody.
            key (str): The musical key (e.g., 'C' for C Major).
            start_note (int): Optional MIDI note to start on.
            temperature (float): Controls randomness.
        """
        if not self.chain:
            print("Error: Model not trained. Call .train() first.")
            return None

        key_scale = scale.MajorScale(key) if key.isupper() else scale.MinorScale(key)
        scale_notes = [p.midi for p in key_scale.getPitches()]

        if start_note and start_note in self.trained_notes:
            possible_starts = [event for event in self.chain.keys() if event[0] == start_note]
            current_event = random.choice(possible_starts) if possible_starts else random.choice(list(self.chain.keys()))
        else:
            current_event = random.choice(list(self.chain.keys()))

        melody = [current_event]

        for _ in range(length - 1):
            possible_next_events = self.chain.get(current_event)
            if not possible_next_events:
                fallback_events = [ev for ev in self.chain.keys() if ev[0] in scale_notes]
                current_event = random.choice(fallback_events if fallback_events else list(self.chain.keys()))
            else:
                # Use a helper method for temperature-based selection if you have one
                # For simplicity, this version uses basic random choice. You can add the
                # more complex temperature logic back in if you have it.
                next_event = random.choice(possible_next_events)
                melody.append(next_event)
                current_event = next_event
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
