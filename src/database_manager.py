# In src/database_manager.py
# FINAL, COMPLETE, AND VERIFIED VERSION

import sqlite3
import json
from pathlib import Path
from werkzeug.security import generate_password_hash

DB_FILE_PATH = Path(__file__).parent.parent / "compositions.db"

def create_database():
    """Initializes the database with a single, unified compositions table."""
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
            composition_type TEXT NOT NULL, -- 'solo', 'ensemble', or 'custom'
            key TEXT, mode TEXT, mood TEXT, bars INTEGER,
                   
            filename_midi TEXT, 
            filename_xml TEXT,
                   
            instrument TEXT, -- For solo/custom, this is the main instrument. For ensemble, the lead.
            accomp_instrument TEXT, -- NULL for non-ensemble pieces
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    """)
    conn.commit()
    conn.close()
    print("Database with unified schema initialized.")

# --- User Management Functions ---
def create_user(username, password):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, generate_password_hash(password)))
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

# --- SEPARATE Save Functions for Each Feature ---
def save_solo_composition(user_id, title, key, mode, mood, bars, instrument, filename_midi, filename_xml):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO compositions (user_id, title, composition_type, key, mode, mood, bars, instrument, filename_midi, filename_xml)
        VALUES (?, ?, 'solo', ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, title, key, mode, mood, bars, instrument, filename_midi, filename_xml))
    conn.commit()
    conn.close()

def save_ensemble_composition(user_id, title, key, mode, mood, bars, lead_instrument, accomp_instrument, filename_midi, filename_xml):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO compositions (user_id, title, composition_type, key, mode, mood, bars, instrument, accomp_instrument, filename_midi, filename_xml)
        VALUES (?, ?, 'ensemble', ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, title, key, mode, mood, bars, lead_instrument, accomp_instrument, filename_midi, filename_xml))
    conn.commit()
    conn.close()

def save_custom_composition(user_id, title, key, mode, bars, instrument, filename_midi, filename_xml):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    # The SQL now correctly includes filename_xml
    cursor.execute("""
        INSERT INTO compositions (user_id, title, composition_type, key, mode, bars, instrument, filename_midi, filename_xml, mood)
        VALUES (?, ?, 'custom', ?, ?, ?, ?, ?, ?, 'custom')
    """, (user_id, title, key, mode, bars, instrument, filename_midi, filename_xml))
    conn.commit()
    conn.close()

# --- UNIFIED Load and Delete Functions ---
def load_compositions_for_user(user_id):
    conn = sqlite3.connect(DB_FILE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM compositions WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
    compositions = cursor.fetchall()
    conn.close()
    return compositions

def get_composition_by_id(comp_id, user_id):
    conn = sqlite3.connect(DB_FILE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM compositions WHERE id = ? AND user_id = ?", (comp_id, user_id))
    composition = cursor.fetchone()
    conn.close()
    return composition

def delete_composition(comp_id, user_id):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM compositions WHERE id = ? AND user_id = ?", (comp_id, user_id))
    conn.commit()
    conn.close()