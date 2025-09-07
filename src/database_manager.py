import sqlite3
import json
from pathlib import Path
from werkzeug.security import generate_password_hash

DB_FILE_PATH = Path(__file__).parent.parent / "compositions.db"

def create_database():
    """Initializes the database and creates tables with the FINAL, CORRECT schema."""
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compositions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            instrument TEXT DEFAULT 'salamander-piano',
            mood TEXT DEFAULT 'default',
            melody_data TEXT NOT NULL,
            chord_data TEXT NOT NULL,
            key TEXT NOT NULL,
            mode TEXT NOT NULL,
            bars INTEGER NOT NULL,
            filename TEXT NOT NULL,
            is_ensemble INTEGER DEFAULT 0, -- 0 for solo, 1 for ensemble
            accomp_instrument TEXT,        -- Will be NULL for solo pieces
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    """)
    conn.commit()
    conn.close()
    print("Database with FINAL users and upgraded compositions tables initialized.")

def create_user(username, password):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, generate_password_hash(password))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_by_username(username):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def save_composition(user_id, title, melody_events, chord_names, key, mode, instrument, mood, bars, filename):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO compositions (user_id, title, melody_data, chord_data, key, instrument, mood, mode, bars, filename)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, title, json.dumps(melody_events), json.dumps(chord_names), key, instrument, mood, mode, bars, filename))
    conn.commit()
    conn.close()


def save_ensemble_composition(user_id, title, melody_events, chord_names, key, mode, 
                              lead_instrument, accomp_instrument, mood, bars, filename):
    """
    Saves a new ENSEMBLE composition to the database.
    """
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    
    melody_json = json.dumps(melody_events)
    chords_json = json.dumps(chord_names)
    
    cursor.execute("""
        INSERT INTO compositions (
            user_id, title, melody_data, chord_data, key, mode, 
            instrument, mood, bars, filename,
            is_ensemble, accomp_instrument
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, title, melody_json, chords_json, key, mode,
        lead_instrument, mood, bars, filename,
        1, # Set is_ensemble to 1 (True) for this piece
        accomp_instrument
    ))
    conn.commit()
    conn.close()



def load_compositions_for_user(user_id):
    """
    Loads all compositions for a user, now including ensemble-specific data.
    """
    conn = sqlite3.connect(DB_FILE_PATH)
    # Using sqlite3.Row allows us to access columns by name (e.g., comp['title'])
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    # Select all the new columns
    cursor.execute("""
        SELECT id, title, key, mode, timestamp, 
               instrument, accomp_instrument, is_ensemble, mood
        FROM compositions 
        WHERE user_id = ? 
        ORDER BY timestamp DESC
    """, (user_id,))
    
    compositions = cursor.fetchall()
    conn.close()
    return compositions
