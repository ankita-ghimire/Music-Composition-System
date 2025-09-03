

import random
import os
from mido import MidiFile, MidiTrack, Message
from music21 import scale

# --- HELPER FUNCTION: Saves the melody to a file ---
# This function is not part of the class, it's a standalone tool.

def save_melody_to_midi(melody_events, filename):
    """
    Saves a melody (list of event tuples) to a MIDI file.
    """
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    print(f"Saving melody to {filename}...")

    # A fixed duration for each note to sound out (in MIDI ticks)
    NOTE_DURATION_TICKS = 240 

    for note, pause_before_note_ticks in melody_events:
        # Note On: velocity=64 (medium volume), time=pause from the last event
        track.append(Message('note_on', note=int(note), velocity=64, time=int(pause_before_note_ticks)))
        # Note Off: The note sounds for NOTE_DURATION_TICKS
        track.append(Message('note_off', note=int(note), velocity=64, time=NOTE_DURATION_TICKS))

    mid.save(filename)
    print("File saved successfully.")


# --- THE MAIN ENGINE CLASS ---
# All the logic for creating melodies is contained in here.

class MelodyGenerator:
    """
    A class to generate melodies using a Markov chain, trained on MIDI files.
    """
    # 1. THE CONSTRUCTOR (runs when you create an instance)
    def __init__(self):
        """Initializes the generator."""
        self.chain = {}
        self.trained_notes = []

    # 2. PUBLIC METHODS (the main tools your friend will use)
    def train(self, midi_folder_path):
        """
        Trains the Markov model on all MIDI files in a given folder.
        """
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

    def generate(self, length, key='C', start_note=None):
        """
        Generates a new melody, biased towards a specific musical key.
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
                in_scale_options = [ev for ev in possible_next_events if ev[0] in scale_notes]
                if in_scale_options and random.random() < 0.8: # 80% chance to stick to the key
                    next_event = random.choice(in_scale_options)
                else:
                    next_event = random.choice(possible_next_events)
                melody.append(next_event)
                current_event = next_event
        return melody

    # 3. "PRIVATE" HELPER METHODS (used internally by the class)
    def _get_musical_events_from_midi(self, file_path):
        """Extracts (note, duration) tuples from a MIDI file."""
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


# --- SCRIPT EXECUTION ---
# This block runs only when you execute this file directly.

if __name__ == "__main__":
    # 1. Create an instance of the melody engine
    melody_engine = MelodyGenerator()

    # 2. Train the engine on your folder of MIDI files
    melody_engine.train("training_data")

    # 3. Generate a new 100-note melody in the key of C Major
    new_melody = melody_engine.generate(100, key='C')

    # 4. If a melody was created, print it and save it to a file
    if new_melody:
        print("\n--- Generated Melody Data ---")
        print(new_melody)
        
        # 5. Save the result so you can listen to it
        save_melody_to_midi(new_melody, "output/ai_melody_final.mid")