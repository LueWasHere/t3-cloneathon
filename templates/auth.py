# File: auth.py

import uuid
from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user, UserMixin
import sqlite3
import os
from datetime import datetime

# --- Database Configuration ---
DB_DIR = 'db'
USER_DB_PATH = os.path.join(DB_DIR, 'user.db')

def get_user_db_conn():
    """Establishes a connection to the user SQLite database."""
    conn = sqlite3.connect(USER_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- User Model for Flask-Login ---
class User(UserMixin):
    def __init__(self, id, email, name, subscription_plan):
        self.id = id
        self.email = email
        self.name = name
        self.subscription_plan = subscription_plan

    @staticmethod
    def get(user_id):
        conn = get_user_db_conn()
        user_data = conn.execute(
            'SELECT * FROM user_accounts WHERE user_id = ?', (user_id,)
        ).fetchone()
        conn.close()
        if not user_data:
            return None
        
        user = User(
            id=user_data['user_id'], 
            email=user_data['email'], 
            name=user_data['name'],
            subscription_plan=user_data['subscription_plan']
        )
        return user

# --- Auth Blueprint ---
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_user_db_conn()
        user_data = conn.execute(
            'SELECT * FROM user_accounts WHERE email = ?', (email,)
        ).fetchone()
        
        if not user_data or not check_password_hash(user_data['hashed_password'], password):
            flash('Please check your login details and try again.', 'error')
            conn.close()
            return redirect(url_for('auth.login'))
        
        conn.close()
        user_obj = User.get(user_data['user_id'])
        login_user(user_obj, remember=True)
        
        return redirect(url_for('index'))
        
    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        password2 = request.form.get('password2') # Get the second password

        if password != password2:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.signup'))

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return redirect(url_for('auth.signup'))
        
        conn = get_user_db_conn()
        try:
            user_data = conn.execute(
                'SELECT user_id FROM user_accounts WHERE email = ?', (email,)
            ).fetchone()
            
            if user_data:
                flash('Email address already exists.', 'error')
                return redirect(url_for('auth.signup'))
            
            new_user_id = str(uuid.uuid4())
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            
            conn.execute(
                '''INSERT INTO user_accounts (user_id, email, name, hashed_password)
                   VALUES (?, ?, ?, ?)''',
                (new_user_id, email, name, hashed_password)
            )
            conn.commit()

            user_obj = User.get(new_user_id)
            login_user(user_obj, remember=True)
            return redirect(url_for('index'))
        finally:
            conn.close()

    return render_template('signup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))