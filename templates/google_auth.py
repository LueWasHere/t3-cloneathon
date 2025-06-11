# File: google_auth.py

import os
import uuid
import sqlite3
from datetime import datetime
from flask import Blueprint, request, redirect, url_for, flash, current_app
from flask import session as flask_session # For session access
from flask_login import login_user # current_user is not directly used here but good to have if needed
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized
import json

# Import the User class from auth.py
from auth import User # Assuming auth.py is in the same directory or Python path

# --- Database Configuration ---
DB_DIR = 'db'
USER_DB_PATH = os.path.join(DB_DIR, 'user.db')

def get_user_db_conn():
    """Establishes a connection to the user SQLite database."""
    conn = sqlite3.connect(USER_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- Create Google OAuth Blueprint ---
def create_google_blueprint():
    """Create and configure the Google OAuth blueprint"""
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

    if not google_client_id or not google_client_secret:
        print("WARNING: Google OAuth credentials not found in environment variables.")
        print("Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your .env file")
        return None

    google_bp = make_google_blueprint(
        client_id=google_client_id,
        client_secret=google_client_secret,
        scope=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile"
        ],
        # No 'redirect_url' here: let Flask-Dance use its default, e.g., /auth/google/authorized
        # This default MUST be in your Google Cloud Console authorized redirect URIs.
    )
    return google_bp

# --- OAuth Token Storage (Simple SQLite Implementation) ---
def create_oauth_table():
    conn = get_user_db_conn()
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS oauth_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                token TEXT NOT NULL,
                user_id VARCHAR(255),
                FOREIGN KEY (user_id) REFERENCES user_accounts (user_id)
            )
        ''')
        conn.commit()
    finally:
        conn.close()

def store_oauth_token(provider, token, user_id=None):
    conn = get_user_db_conn()
    try:
        if user_id:
            conn.execute(
                'DELETE FROM oauth_tokens WHERE provider = ? AND user_id = ?',
                (provider, user_id)
            )
        conn.execute(
            'INSERT INTO oauth_tokens (provider, token, user_id) VALUES (?, ?, ?)',
            (provider, json.dumps(token), user_id)
        )
        conn.commit()
    finally:
        conn.close()

def get_oauth_token(provider, user_id=None): # Not actively used in this flow, but good utility
    conn = get_user_db_conn()
    try:
        query = 'SELECT token FROM oauth_tokens WHERE provider = ? '
        params = [provider]
        if user_id:
            query += 'AND user_id = ? '
            params.append(user_id)
        query += 'ORDER BY created_at DESC LIMIT 1'
        
        result = conn.execute(query, tuple(params)).fetchone()
        if result:
            return json.loads(result['token'])
        return None
    finally:
        conn.close()

# --- Google Authentication Functions ---
def get_google_user_info():
    if not google.authorized:
        print("DEBUG: get_google_user_info - Google session not authorized.")
        return None
    try:
        resp = google.get("/oauth2/v2/userinfo")
        if not resp.ok:
            print(f"DEBUG: Failed to fetch user info from Google: {resp.status_code} - {resp.text}")
            return None
        google_info = resp.json()
        print(f"DEBUG: Received Google user info: {google_info}")
        return {
            'google_id': google_info.get('id'),
            'email': google_info.get('email'),
            'name': google_info.get('name'),
            'first_name': google_info.get('given_name'),
            'last_name': google_info.get('family_name'),
            'picture': google_info.get('picture'),
            'verified_email': google_info.get('verified_email', False)
        }
    except Exception as e:
        print(f"DEBUG: Error in get_google_user_info: {e}")
        return None

def find_user_by_email(email):
    conn = get_user_db_conn()
    try:
        user_data = conn.execute(
            'SELECT * FROM user_accounts WHERE email = ?', (email,)
        ).fetchone()
        if user_data:
            return User(
                id=user_data['user_id'],
                email=user_data['email'],
                name=user_data['name'],
                subscription_plan=user_data['subscription_plan']
            )
        return None
    finally:
        conn.close()

def create_user_from_google(google_info):
    conn = get_user_db_conn()
    try:
        new_user_id = str(uuid.uuid4())
        conn.execute(
            '''INSERT INTO user_accounts (user_id, email, name, hashed_password, google_id, created_at, subscription_plan)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (
                new_user_id,
                google_info['email'],
                google_info['name'],
                None,
                google_info['google_id'],
                datetime.now().isoformat(),
                'free'
            )
        )
        conn.commit()
        print(f"DEBUG: User {new_user_id} created in DB with email {google_info['email']}")
        return User.get(new_user_id)
    except sqlite3.IntegrityError as e:
        print(f"DEBUG: IntegrityError creating user (email: {google_info['email']}): {e}. User might already exist.")
        return find_user_by_email(google_info['email']) # Try to fetch if exists due to race or similar
    except Exception as e:
        print(f"DEBUG: General error creating user (email: {google_info['email']}): {e}")
        return None
    finally:
        conn.close()

def update_user_google_info(user, google_info):
    conn = get_user_db_conn()
    try:
        current_db_user = conn.execute('SELECT google_id, name FROM user_accounts WHERE user_id = ?', (user.id,)).fetchone()
        if current_db_user and \
           (current_db_user['google_id'] != google_info['google_id'] or \
            current_db_user['name'] != google_info['name']):
            conn.execute(
                '''UPDATE user_accounts SET google_id = ?, name = ? WHERE user_id = ?''',
                (google_info['google_id'], google_info['name'], user.id)
            )
            conn.commit()
            print(f"DEBUG: User {user.id} Google info updated in DB.")
        else:
            print(f"DEBUG: User {user.id} Google info already up-to-date or no change needed.")
    except Exception as e:
        print(f"DEBUG: Error updating Google info for user {user.id}: {e}")
    finally:
        conn.close()

# --- OAuth Event Handlers ---
@oauth_authorized.connect
def google_logged_in(blueprint, token):
    print("DEBUG: google_logged_in signal handler called.")
    if not token:
        flash('Failed to log in with Google (no token received).', 'error')
        print("DEBUG: No token received in google_logged_in.")
        return False

    store_oauth_token('google', token) # Store token temporarily
    print(f"DEBUG: Initial token stored: {str(token)[:200]}...") # Print truncated token

    google_info = get_google_user_info()
    if not google_info:
        flash('Failed to fetch user information from Google.', 'error')
        print("DEBUG: Failed to get google_info in google_logged_in.")
        return False

    if not google_info.get('verified_email'):
        flash('Google account email is not verified. Please verify your email with Google and try again.', 'error')
        print("DEBUG: Google email not verified.")
        return False

    user_email = google_info['email']
    user = find_user_by_email(user_email)
    print(f"DEBUG: find_user_by_email('{user_email}') returned: {user}")

    if user:
        update_user_google_info(user, google_info)
        store_oauth_token('google', token, user.id) # Re-store with user_id
        print(f"DEBUG: Existing user {user.id} ({user.email}) processed.")
    else:
        user = create_user_from_google(google_info)
        if not user:
            flash('Failed to create a user account from Google information.', 'error')
            print("DEBUG: Failed to create user from Google info in google_logged_in.")
            return False
        store_oauth_token('google', token, user.id) # Store with new user_id
        print(f"DEBUG: New user {user.id} ({user.email}) created and processed.")

    try:
        login_user(user, remember=True)
        flash(f'Successfully logged in as {user.name} with Google!', 'success')
        print(f"DEBUG: User {user.email} (ID: {user.id}) logged in with Flask-Login.")
    except Exception as e:
        flash('Error during login process after Google authentication.', 'error')
        print(f"DEBUG: Exception during login_user for '{user.email if user else 'UnknownUser'}': {e}")
        return False

    # --- Next URL Handling ---
    # Flask-Dance uses a specific key in Flask's session for its own 'next' logic
    # The key is usually f"{blueprint.name}_oauth_next_url"
    flask_dance_next_key = f"{blueprint.name}_oauth_next_url"
    next_url_from_flask_dance_session_storage = flask_session.get(flask_dance_next_key)

    # Standard Flask-Login 'next' often comes from request.args when /login is hit
    next_url_from_flask_login = flask_session.get("next")

    print(f"DEBUG: flask_session.get('{flask_dance_next_key}') = {next_url_from_flask_dance_session_storage}")
    print(f"DEBUG: flask_session.get('next') = {next_url_from_flask_login}")

    # Clear these to prevent unintended redirects by Flask-Dance or Flask-Login's default behavior
    # after this signal handler returns. We want a clean redirect, likely to app root.
    if flask_dance_next_key in flask_session:
        print(f"DEBUG: Deleting '{flask_dance_next_key}' ('{flask_session.get(flask_dance_next_key)}') from flask_session")
        del flask_session[flask_dance_next_key]

    if "next" in flask_session: # This 'next' is often set by @login_required
        print(f"DEBUG: Deleting 'next' ('{flask_session.get('next')}') from flask_session")
        del flask_session["next"]

    # `blueprint.session.params` might contain state info, but manipulating it here is less direct.
    # Clearing from flask_session should be sufficient for post-auth redirect.

    print("DEBUG: google_logged_in returning False. Flask-Dance will now handle the redirect.")
    # Returning False tells Flask-Dance's 'authorized' view to take over.
    # It should redirect to the application root or a sensible default.
    return False

# --- Initialize Google Auth ---
def init_google_auth(app):
    create_oauth_table()
    conn = get_user_db_conn()
    try:
        cursor = conn.execute("PRAGMA table_info(user_accounts)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'google_id' not in columns:
            print("Adding google_id column to user_accounts table...")
            conn.execute('ALTER TABLE user_accounts ADD COLUMN google_id VARCHAR(255)')
            conn.commit()
            print("Google ID column added successfully.")
        if 'subscription_plan' not in columns:
            print("Adding subscription_plan column to user_accounts table...")
            conn.execute("ALTER TABLE user_accounts ADD COLUMN subscription_plan VARCHAR(50) DEFAULT 'free'")
            conn.commit()
            print("Subscription plan column added successfully.")
    except Exception as e:
        print(f"Error checking/adding columns to user_accounts table: {e}")
    finally:
        conn.close()

    google_bp = create_google_blueprint()
    if google_bp:
        app.register_blueprint(google_bp, url_prefix="/auth")
        print("Google OAuth blueprint registered successfully.")
        return True
    else:
        print("Google OAuth blueprint not registered (missing credentials or other error).")
        return False

# --- Utility Functions ---
def is_google_oauth_configured():
    return bool(os.getenv('GOOGLE_CLIENT_ID') and os.getenv('GOOGLE_CLIENT_SECRET'))

def get_google_login_url():
    if is_google_oauth_configured():
        try:
            # 'google.login' refers to the 'login' view within the blueprint named 'google'.
            return url_for('google.login')
        except Exception as e:
            print(f"DEBUG: Error generating Google login URL (is blueprint registered correctly?): {e}")
            return None
    return None