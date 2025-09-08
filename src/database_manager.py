# In src/database_manager.py
# FINAL, UNIFIED, AND VERIFIED VERSION
# This manager handles users and all three types of compositions.

import sqlite3
import json
from pathlib import Path
from werkzeug.security import generate_password_hash

# Define the database path to be in the project's root folder
DB_FILE_PATH = Path(__file__).parent.parent / "compositions.db"

def create_database():
    """
    Initializes the database and creates the FINAL, unified tables for users and compositions.
    """
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    
    # --- Users Table (Unchanged) ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        );
    """)
    
    # --- Compositions Table (Final, Unified Schema) ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compositions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            
            -- This is the key to separating features
            composition_type TEXT NOT NULL, -- 'solo', 'ensemble', or 'custom'
            
            -- Columns for all types
            key TEXT,
            mode TEXT,
            mood TEXT,
            bars INTEGER,
            filename TEXT,
            
            -- Columns for SOLO and ENSEMBLE
            instrument TEXT, -- For solo, this is the main instrument. For ensemble, the lead.
            
            -- Columns ONLY for ENSEMBLE
            accomp_instrument TEXT, -- Will be NULL for non-ensemble pieces
            
            -- Columns for storing the raw AI data
            melody_data TEXT,
            chord_data TEXT,
            
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    """)
    conn.commit()
    conn.close()
    print("Database with unified schema initialized.")

# ==============================================================================
# User Management Functions (Complete and Correct)
# ==============================================================================
def create_user(username, password):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, generate_password_hash(password)))
        conn.commit(); return True
    except sqlite3.IntegrityError: return False
    finally: conn.close()

def get_user_by_username(username):
    conn = sqlite3.connect(DB_FILE_PATH); cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone(); conn.close(); return user

# ==============================================================================
# SEPARATE Save Functions for Each Feature
# ==============================================================================

def save_solo_composition(user_id, title, key, mode, mood, bars, instrument, filename, melody_data, chord_data):
    """Saves a SOLO composition to the database."""
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO compositions (user_id, title, composition_type, key, mode, mood, bars, instrument, filename, melody_data, chord_data)
        VALUES (?, ?, 'solo', ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, title, key, mode, mood, bars, instrument, filename, json.dumps(melody_data), json.dumps(chord_data)))
    conn.commit()
    conn.close()

def save_ensemble_composition(user_id, title, key, mode, mood, bars, lead_instrument, accomp_instrument, filename, melody_data, chord_data):
    """Saves an ENSEMBLE composition to the database."""
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO compositions (user_id, title, composition_type, key, mode, mood, bars, instrument, accomp_instrument, filename, melody_data, chord_data)
        VALUES (?, ?, 'ensemble', ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, title, key, mode, mood, bars, lead_instrument, accomp_instrument, filename, json.dumps(melody_data), json.dumps(chord_data)))
    conn.commit()
    conn.close()

def save_custom_composition(user_id, title, key, mode, bars, instrument, filename, melody_data, chord_data):
    """Saves a CUSTOM PROGRESSION composition to the database."""
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    # Note: 'mood' is not applicable for custom, so we can omit it or save a default
    cursor.execute("""
        INSERT INTO compositions (user_id, title, composition_type, key, mode, bars, instrument, filename, melody_data, chord_data, mood)
        VALUES (?, ?, 'custom', ?, ?, ?, ?, ?, ?, ?, 'custom')
    """, (user_id, title, key, mode, bars, instrument, filename, json.dumps(melody_data), json.dumps(chord_data)))
    conn.commit()
    conn.close()


# ==============================================================================
# UNIFIED Load Functions
# ==============================================================================

def load_compositions_for_user(user_id):
    """Loads all compositions for a specific user to display on their page."""
    conn = sqlite3.connect(DB_FILE_PATH)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name in the template
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM compositions WHERE user_id = ? ORDER BY timestamp DESC", 
        (user_id,)
    )
    compositions = cursor.fetchall()
    conn.close()
    return compositions


def load_composition_by_id(comp_id):
    """Loads the full data for a single composition by its ID."""
    conn = sqlite3.connect(DB_FILE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM compositions WHERE id = ?", (comp_id,))
    composition = cursor.fetchone()
    conn.close()
    # The calling function will need to handle the JSON parsing
    return composition