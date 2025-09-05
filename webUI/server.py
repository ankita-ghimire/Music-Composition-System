import os
import sys
from flask import Flask, render_template, request, send_from_directory, jsonify, session, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from pathlib import Path

# --- Backend Setup ---
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from main import generate_composition
    import database_manager as db
except ImportError as e:
    print(f"Error: Could not import a required module: {e}")
    sys.exit(1)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key_change_this'
app.config['OUTPUT_FOLDER'] = os.path.abspath(os.path.join(backend_path, 'output'))
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# --- Database Initialization ---
db.create_database()

# --- Page Rendering Routes ---

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/compose")
def compose_page():
    if 'user_id' not in session:
        flash("You need to be logged in to compose music.", "warning")
        return redirect(url_for('login'))
    return render_template("compose.html")

# ... (other main page routes are correct)

# --- User Authentication Routes (THIS IS THE MISSING PART) ---

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        if db.get_user_by_username(username):
            flash("Username already exists.", "warning")
        elif db.create_user(username, password):
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for('login'))
        else:
            flash("An error occurred. Please try again.", "danger")
            
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = db.get_user_by_username(username)
        
        # user[2] should be the password_hash column from your database
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0] # user[0] is the id
            session['username'] = user[1] # user[1] is the username
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

# --- (The rest of your server.py file) ---
# ...