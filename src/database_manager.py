# In src/database_manager.py
import sqlite3
import json # We'll store the melody/chord data as JSON text

DATABASE_NAME = "compositions.db"

def create_database():
    """Initializes the database and creates the compositions table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compositions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            melody_data TEXT NOT NULL,
            chord_data TEXT NOT NULL,
            key TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def save_composition(name, melody_events, chord_sequence, key):
    """Saves a new composition to the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    # Convert the Python lists to JSON strings for storage
    melody_json = json.dumps(melody_events)
    chords_json = json.dumps(chord_sequence) # Assuming chords will be a list of strings
    
    cursor.execute("""
        INSERT INTO compositions (name, melody_data, chord_data, key)
        VALUES (?, ?, ?, ?)
    """, (name, melody_json, chords_json, key))
    
    conn.commit()
    conn.close()
    print(f"Composition '{name}' saved successfully.")

def load_all_compositions():
    """Loads all saved composition names and IDs from the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, timestamp FROM compositions ORDER BY timestamp DESC")
    compositions = cursor.fetchall()
    conn.close()
    return compositions # Returns a list of (id, name, timestamp) tuples

# You would also create a function like load_composition_by_id(id) later