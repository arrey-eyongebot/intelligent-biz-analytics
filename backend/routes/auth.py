# ============================================================
# routes/auth.py — User Authentication Routes
#
# Handles user registration, login, logout and session
# management. User credentials are stored in a simple JSON
# file for this project (no external database needed).
#
# Endpoints:
#   POST /api/auth/register — Create a new account
#   POST /api/auth/login    — Login with email and password
#   POST /api/auth/logout   — Clear the session
#   GET  /api/auth/status   — Check if user is logged in
# ============================================================

from flask import Blueprint, request, jsonify, session
import json
import os
import hashlib  # For hashing passwords securely

auth_bp = Blueprint('auth', __name__)

# Path to the file storing registered users
# In a real production system this would be a database
USERS_FILE = os.path.join(
    os.path.dirname(__file__), '..', '..', 'data', 'users.json'
)


def load_users():
    """
    Loads all registered users from the JSON file.
    Returns an empty dict if no users have registered yet.
    """
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_users(users):
    """
    Saves the users dictionary back to the JSON file.
    Creates the data directory if it does not exist yet.
    """
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)


def hash_password(password):
    """
    Hashes a password using SHA-256 for secure storage.
    We never store plain text passwords.

    Parameters:
        password (str): Plain text password from the form

    Returns:
        str: Hashed password string
    """
    return hashlib.sha256(password.encode()).hexdigest()


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    POST /api/auth/register
    Creates a new user account.

    Required request body:
    {
        "name":     "Brian Arrey",
        "email":    "brian@example.com",
        "password": "mypassword"
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    name     = data.get('name',     '').strip()
    email    = data.get('email',    '').strip().lower()
    password = data.get('password', '').strip()

    # Validate all fields are provided
    if not name or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    # Validate password length
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    # Load existing users
    users = load_users()

    # Check if email is already registered
    if email in users:
        return jsonify({'error': 'An account with this email already exists'}), 400

    # Save new user with hashed password
    users[email] = {
        'name':     name,
        'email':    email,
        'password': hash_password(password)
    }
    save_users(users)

    # Automatically log in after registration
    session['user'] = {'name': name, 'email': email}

    return jsonify({
        'message': f'Account created successfully! Welcome, {name}.',
        'user':    {'name': name, 'email': email}
    }), 200


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    POST /api/auth/login
    Authenticates a user and creates a session.

    Required request body:
    {
        "email":    "brian@example.com",
        "password": "mypassword"
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email    = data.get('email',    '').strip().lower()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    # Load users and check if email exists
    users = load_users()
    if email not in users:
        return jsonify({'error': 'Invalid email or password'}), 401

    # Compare hashed passwords
    if users[email]['password'] != hash_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Create session for the logged-in user
    user = {'name': users[email]['name'], 'email': email}
    session['user'] = user

    return jsonify({
        'message': f'Welcome back, {user["name"]}!',
        'user':    user
    }), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    POST /api/auth/logout
    Clears the user session (logs out).
    """
    session.pop('user', None)
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/status', methods=['GET'])
def status():
    """
    GET /api/auth/status
    Returns whether the user is currently logged in.
    Called by every protected page on load to check auth.

    Returns:
    {
        "logged_in": true,
        "user": { "name": "Brian", "email": "..." }
    }
    """
    if 'user' in session:
        return jsonify({
            'logged_in': True,
            'user':      session['user']
        }), 200
    return jsonify({'logged_in': False}), 200