from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import bcrypt

# Load .env file
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Initialize Flask app
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Replace this with a secure random key

# Init JWT
jwt = JWTManager(app)

# MongoDB client
client = MongoClient(MONGO_URI)
db = client['music_app']
users = db['users']

# ✅ Register Route
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if users.find_one({'username': username}):
        return jsonify({"msg": "User already exists"}), 409

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users.insert_one({'username': username, 'password': hashed})

    return jsonify({"msg": "User registered successfully"}), 201

# ✅ Login Route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = users.find_one({'username': username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Invalid credentials"}), 401

# ✅ Protected route (test)
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# Run server
if __name__ == '__main__':
    app.run(debug=True)
