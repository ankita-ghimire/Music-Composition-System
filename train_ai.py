
import pickle
from pathlib import Path
from melody_generator import MelodyGenerator

print("--- Starting AI Model Training (This may take a few minutes)... ---")
melody_engine = MelodyGenerator()
training_data_path = Path(__file__).parent / "training_data"

if training_data_path.exists():
    melody_engine.train(str(training_data_path))
    with open("trained_model.pkl", "wb") as f:
        pickle.dump(melody_engine.chain, f)
    print("\n--- SUCCESS! AI model trained and saved to 'trained_model.pkl'. ---")
else:
    print("FATAL: 'training_data' folder not found.")