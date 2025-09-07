import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

# The database file will be created in the project's root folder.
DB_FILE_PATH = Path(__file__).parent.parent / "compositions.db"

def create_database():
    """Initializes the database and creates tables with the FINAL, CORRECT schema."""
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    # --- Users Table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        );
    """)
    # --- Compositions Table (with all necessary columns for all features) ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compositions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            key TEXT NOT NULL,
            mode TEXT NOT NULL,
            bars INTEGER NOT NULL,
            filename_midi TEXT NOT NULL,
            filename_xml TEXT NOT NULL,
            instrument TEXT NOT NULL,
            accomp_instrument TEXT,
            is_ensemble INTEGER NOT NULL DEFAULT 0,
            mood TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    """)
    conn.commit()
    conn.close()
    print("Database with FINAL users and ENSEMBLE compositions tables initialized.")

# --- User Management Functions ---
def create_user(username, password):
    """Creates a new user with a hashed password."""
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
    """Retrieves a user's data by their username."""
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

# --- Composition Management Functions ---
def save_composition(user_id, title, key, mode, bars, filename_midi, filename_xml, instrument, mood, is_ensemble, accomp_instrument):
    """Saves a composition, correctly handling both solo and ensemble types."""
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO compositions (user_id, title, key, mode, bars, filename_midi, filename_xml, instrument, mood, is_ensemble, accomp_instrument)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, title, key, mode, bars, filename_midi, filename_xml, instrument, mood, is_ensemble, accomp_instrument))
    conn.commit()
    conn.close()

def load_compositions_for_user(user_id):
    """Loads all compositions for a user, allowing access to columns by name."""
    conn = sqlite3.connect(DB_FILE_PATH)
    conn.row_factory = sqlite3.Row # This is important for the templates!
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM compositions WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
    compositions = cursor.fetchall()
    conn.close()
    return compositions

def get_composition_by_id(comp_id, user_id):
    """Fetches a single composition to ensure the user owns it (for the play button)."""
    conn = sqlite3.connect(DB_FILE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM compositions WHERE id = ? AND user_id = ?", (comp_id, user_id))
    composition = cursor.fetchone()
    conn.close()
    return composition