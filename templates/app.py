# Updated app.py - Replace the existing app.py with this version

from flask import Flask, render_template, request, jsonify, send_from_directory, abort
from flask_login import LoginManager, login_required, current_user
import random
import time
import os
import sqlite3
import re
from datetime import timedelta
from functools import wraps
from dotenv import load_dotenv

# Import our new AI client
from ai_client import AIClient

# --- Load Environment Variables ---
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)

# --- Google OAuth Configuration ---
app.config['GOOGLE_OAUTH_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_OAUTH_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')

# --- Database Configuration ---
DB_DIR = 'db'
DB_PATH = os.path.join(DB_DIR, 'models.db')
USER_DB_PATH = os.path.join(DB_DIR, 'user.db')

# Initialize AI Client
ai_client = None

def check_db_exists():
    """Checks if the models database file exists."""
    if not os.path.exists(DB_PATH):
        print("="*60)
        print(f"FATAL ERROR: Database file not found at '{DB_PATH}'")
        print("This application requires a pre-existing database.")
        print("\nPlease create it by running the following command from your")
        print("project's root directory:")
        print("\n    sqlite3 db/models.db < create_db.sql\n")
        print("="*60)
        exit(1)
    print(f"Database found at '{DB_PATH}'. Starting application.")

def check_user_db_exists():
    """Checks if the user database file exists."""
    if not os.path.exists(USER_DB_PATH):
        print("="*60)
        print(f"FATAL ERROR: User database file not found at '{USER_DB_PATH}'")
        print("This application requires a user database.")
        print("\nPlease create it by running the following command from your")
        print("project's root directory:")
        print("\n    sqlite3 db/user.db < create_user_db.sql\n")
        print("="*60)
        exit(1)
    print(f"User database found at '{USER_DB_PATH}'.")

def get_db_conn():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- Authentication Setup ---
from auth import auth as auth_blueprint, User

app.register_blueprint(auth_blueprint)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

try:
    from google_auth import init_google_auth, is_google_oauth_configured, get_google_login_url
    google_auth_enabled = init_google_auth(app)
    if google_auth_enabled:
        print("Google OAuth authentication enabled.")
    else:
        print("Google OAuth authentication disabled (missing credentials).")
except ImportError as e:
    print(f"Google authentication not available: {e}")
    google_auth_enabled = False
except Exception as e:
    print(f"An unexpected error occurred during Google Auth initialization: {e}")
    google_auth_enabled = False

@app.context_processor
def inject_google_auth():
    is_enabled = globals().get('google_auth_enabled', False)
    _url = None
    if is_enabled:
        _url = get_google_login_url()
    return {
        'google_auth_enabled': is_enabled,
        'google_login_url': _url
    }

# --- Admin Authorization Decorator ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
        if not ADMIN_EMAIL:
            print("WARNING: ADMIN_EMAIL not set in .env file. Admin panel is disabled.")
            abort(404)
        if not current_user.is_authenticated:
            return login_manager.unauthorized()
        if current_user.email != ADMIN_EMAIL:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def get_user_db_conn():
    """Establishes a connection to the user SQLite database."""
    conn = sqlite3.connect(USER_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def format_number_with_comma(value):
    """Formats an integer with a comma as a thousands separator."""
    if value is None:
        return '0'
    try:
        return f'{int(value):,}'
    except (ValueError, TypeError):
        return str(value)

app.jinja_env.filters['numberformat'] = format_number_with_comma

@app.route('/settings')
@login_required
def settings():
    """Renders the user settings page with dynamic token usage data."""
    total_tokens = 10000
    conn = get_user_db_conn()
    user_data = conn.execute(
        'SELECT token_quota FROM user_accounts WHERE user_id = ?',
        (current_user.id,)
    ).fetchone()
    conn.close()

    tokens_used = 0
    if user_data and user_data['token_quota'] is not None:
        tokens_used = int(user_data['token_quota'])

    tokens_remaining = total_tokens - tokens_used
    if tokens_remaining < 0:
        tokens_remaining = 0
        
    progress_percentage = 0
    if total_tokens > 0:
        progress_percentage = min(100, (tokens_used / total_tokens) * 100)

    return render_template(
        'settings.html',
        tokens_used=tokens_used,
        total_tokens=total_tokens,
        tokens_remaining=tokens_remaining,
        progress_percentage=progress_percentage
    )

def format_model_data(row):
    """Formats a database row into a dictionary for the frontend."""
    provider_name = row['provider_name']
    model_name = row['model_name']

    provider_key_map = {
        'OpenAI': 'openai',
        'Anthropic': 'claude',
        'Google': 'gemini',
        'xAI': 'grok',
        'DeepSeek': 'deepseek',
        'Together.ai': 'meta',
        'Meta': 'meta'
    }
    provider_key = provider_key_map.get(provider_name, provider_name.lower())
    
    if provider_name == 'Together.ai' and 'meta-llama' in model_name:
        provider_key = 'meta'

    main_name, sub_name = model_name, ''
    
    if 'gpt-4o-mini' in model_name:
        main_name, sub_name = 'GPT-4o', 'Mini'
    elif 'gpt-4o' in model_name:
        main_name, sub_name = 'GPT-4o', ''
    elif 'o1-mini' in model_name:
        main_name, sub_name = 'o1', 'Mini'
    elif 'claude-3.5-sonnet' in model_name:
        main_name, sub_name = 'Claude 3.5', 'Sonnet'
    elif 'claude-3-opus' in model_name:
        main_name, sub_name = 'Claude 3', 'Opus'
    elif 'gemini-1.5-pro' in model_name:
        main_name, sub_name = 'Gemini 1.5', 'Pro'
    elif 'gemini-1.5-flash' in model_name:
        main_name, sub_name = 'Gemini 1.5', 'Flash'
    elif 'deepseek-coder' in model_name:
        main_name, sub_name = 'DeepSeek', 'Coder'
    elif 'Llama-3.1-70B' in model_name:
        main_name, sub_name = 'Llama 3.1', '70B'
    else:
        match = re.match(r'([a-zA-Z0-9\._/]+-?)([\d\.]+[a-zA-Z]*-?instruct|[\d\.]+-?pro|[\d\.]+-?flash|[\d\.]+-?sonnet|[\d\.]+-?opus|[\d\.]+-?haiku|o-?mini|turbo|mini)?', model_name, re.IGNORECASE)
        if match and match.groups()[1]:
            main_name_raw = match.groups()[0].strip('-').replace('meta-llama/Llama', 'Llama').replace('claude-','Claude ')
            sub_name_raw = match.groups()[1].strip('-').replace('-Instruct', '')
            main_name = ' '.join(p.capitalize() for p in main_name_raw.replace('-', ' ').split())
            sub_name = ' '.join(p.capitalize() for p in sub_name_raw.replace('-', ' ').split())

    is_premium = False
    premium_icon = None
    input_price = row['usd_per_million_input_tokens']
    
    if input_price is not None and input_price > 2.5:
        is_premium = True
        if 'opus' in model_name.lower() or '405b' in model_name.lower():
            premium_icon = 'gem'
        elif row['reasoning_enabled']:
            premium_icon = 'key'
        elif 'pro' in model_name.lower() or 'turbo' in model_name.lower() or '70b' in model_name.lower():
            premium_icon = 'flask'

    capabilities = {
        'vision': bool(row['supports_images_input']),
        'reasoning': bool(row['reasoning_enabled']),
        'coding': 'coder' in model_name.lower() or 'codex' in model_name.lower(),
        'web': provider_name.lower() == 'xai',
        'docs': bool(row['supports_pdfs_input']),
    }

    return {
        'name': model_name,
        'api_name': row['api_name'], # <<< ADDED THIS LINE
        'provider': provider_key,
        'displayNameMain': main_name,
        'displayNameSub': sub_name,
        'subtitle': row['notes'],
        'premium': is_premium,
        'premium_icon': premium_icon,
        'capabilities': capabilities,
        'context_window': row['context_window_max_tokens'],
        'input_price': row['usd_per_million_input_tokens'],
        'output_price': row['usd_per_million_output_tokens'],
        'multimodal': bool(row['multimodal_input'])
    }

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    if filename == 'auth.css':
        return send_from_directory('static', 'auth.css')
    return send_from_directory('static', filename)

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    """Handle chat requests with real AI APIs"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        model = data.get('model', 'gpt-4o-mini')
        
        if not message: 
            return jsonify({'error': 'Empty message'}), 400
        
        if not ai_client:
            return jsonify({'error': 'AI client not initialized. Please check your API keys.'}), 500
        
        # Generate response using real AI
        try:
            response = ai_client.generate_response(model, message)
            return jsonify({'response': response})
        except ValueError as e:
            # Model not found or no API client
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            # API error - return a friendly message
            print(f"AI API Error: {e}")
            return jsonify({'error': f'Sorry, I encountered an error while processing your request. Please try again or select a different model.'}), 500
            
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/models')
@login_required
def get_models_data():
    """Fetch all active models from the database - supports multiple table structure"""
    conn = get_db_conn()
    try:
        # Check what tables exist
        tables_query = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%model%'"
        ).fetchall()
        
        table_names = [table['name'] for table in tables_query]
        
        all_models = []
        
        # If we have the new structure (separate tables)
        if 'llm_models' in table_names:
            # Use llm_models as primary table for chat interface
            db_models = conn.execute('''
                SELECT * FROM llm_models 
                WHERE is_active = 1 
                ORDER BY provider_name, usd_per_million_input_tokens DESC
            ''').fetchall()
        # Fallback to old structure
        elif 'models' in table_names:
            db_models = conn.execute('''
                SELECT * FROM models 
                WHERE is_active = 1 
                ORDER BY provider_name, usd_per_million_input_tokens DESC
            ''').fetchall()
        else:
            return jsonify({'error': 'No model tables found in database'}), 500
        
    except sqlite3.OperationalError as e:
        print(f"Error querying database: {e}")
        return jsonify({'error': f"Database query failed: {e}"}), 500
    finally:
        conn.close()

    # Use models that have recognizable names for the popular list
    popular_model_names = [
        'gpt-4o', 'claude-3-5-sonnet-20241022', 'gemini-1.5-pro',
        'Claude Sonnet 4', 'Gemini 2.0 Flash', 'o1-mini'
    ]
    
    popular_models = []
    all_other_models = []

    for row in db_models:
        formatted = format_model_data(row)
        if (row['model_name'] in popular_model_names or 
            any(name.lower() in row['model_name'].lower() for name in popular_model_names)):
            popular_models.append(formatted)
        else:
            all_other_models.append(formatted)
    
    # If no popular models found, take first 6 as popular
    if not popular_models and all_other_models:
        popular_models = all_other_models[:6]
        all_other_models = all_other_models[6:]

    return jsonify({
        'popular': popular_models,
        'all': all_other_models,
    })

@app.route('/models/available')
@login_required
def get_available_models():
    """Get models that have working API clients"""
    if not ai_client:
        return jsonify({'available': []})
    
    available = ai_client.get_available_models()
    return jsonify({'available': available})

# --- Admin Routes (FIXED) ---
@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin.html')

@app.route('/admin/models')
@admin_required
def admin_get_models():
    conn = get_db_conn()
    try:
        models = conn.execute('''
            SELECT * FROM llm_models 
            ORDER BY provider_name, model_name
        ''').fetchall()
        models_list = [dict(model) for model in models]
        return jsonify({'models': models_list})
    except sqlite3.OperationalError as e:
        if "no such table: llm_models" in str(e):
            # Try falling back to the old 'models' table
            try:
                models = conn.execute('SELECT * FROM models ORDER BY provider_name, model_name').fetchall()
                models_list = [dict(model) for model in models]
                return jsonify({'models': models_list})
            except Exception as e_fallback:
                 print(f"Error fetching from fallback 'models' table: {e_fallback}")
                 return jsonify({'error': "Database schema mismatch. 'llm_models' and 'models' tables not found."}), 500
        print(f"Error fetching models for admin: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/admin/providers')
@admin_required
def admin_get_providers():
    conn = get_db_conn()
    try:
        providers_data = conn.execute('''
            SELECT
                provider_name,
                COUNT(id) AS total_models,
                SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active_models
            FROM
                llm_models
            GROUP BY
                provider_name
            ORDER BY
                provider_name
        ''').fetchall()
        providers_list = [dict(p) for p in providers_data]
        return jsonify({'providers': providers_list})
    except Exception as e:
        print(f"Error fetching providers for admin: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/admin/search')
@admin_required
def admin_search_models():
    query = request.args.get('q', '').strip()
    if not query:
        return admin_get_models()
    
    conn = get_db_conn()
    try:
        search_term = f'%{query}%'
        models = conn.execute('''
            SELECT * FROM llm_models
            WHERE model_name LIKE ? OR provider_name LIKE ? OR notes LIKE ?
            ORDER BY provider_name, model_name
        ''', (search_term, search_term, search_term)).fetchall()
        
        models_list = [dict(m) for m in models]
        return jsonify({'models': models_list})
    except Exception as e:
        print(f"Error searching models: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/admin/models', methods=['POST'])
@admin_required
def admin_add_model():
    try:
        data = request.get_json()
        provider_name = data.get('provider_name', '').strip()
        model_name = data.get('model_name', '').strip()
        
        if not provider_name or not model_name:
            return jsonify({'error': 'Provider name and model name are required.'}), 400
        
        conn = get_db_conn()
        try:
            existing = conn.execute('SELECT id FROM llm_models WHERE model_name = ?', (model_name,)).fetchone()
            if existing:
                return jsonify({'error': f'Model "{model_name}" already exists.'}), 400
            
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO llm_models (
                    provider_name, model_name, api_name, context_window_max_tokens,
                    supports_images_input, supports_pdfs_input, multimodal_input,
                    reasoning_enabled, usd_per_million_input_tokens, 
                    usd_per_million_output_tokens, is_active, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                provider_name, model_name, data.get('api_name', model_name),
                data.get('context_window_max_tokens'), bool(data.get('supports_images_input', False)),
                bool(data.get('supports_pdfs_input', False)), bool(data.get('multimodal_input', False)),
                bool(data.get('reasoning_enabled', False)), data.get('usd_per_million_input_tokens'),
                data.get('usd_per_million_output_tokens'), bool(data.get('is_active', True)),
                data.get('notes', '')
            ))
            conn.commit()
            return jsonify({'success': True, 'message': f'Model "{model_name}" added successfully.'})
        finally:
            conn.close()
    except Exception as e:
        print(f"Error adding model: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/models/<int:model_id>', methods=['PUT'])
@admin_required
def admin_update_model(model_id):
    try:
        data = request.get_json()
        conn = get_db_conn()
        try:
            # NOTE: api_name is not updated here as it's not present in the admin form
            conn.execute('''
                UPDATE llm_models SET
                    provider_name = ?, model_name = ?, context_window_max_tokens = ?,
                    supports_images_input = ?, supports_pdfs_input = ?, multimodal_input = ?,
                    reasoning_enabled = ?, usd_per_million_input_tokens = ?,
                    usd_per_million_output_tokens = ?, is_active = ?, notes = ?
                WHERE id = ?
            ''', (
                data.get('provider_name'), data.get('model_name'),
                data.get('context_window_max_tokens'), bool(data.get('supports_images_input')),
                bool(data.get('supports_pdfs_input')), bool(data.get('multimodal_input')),
                bool(data.get('reasoning_enabled')), data.get('usd_per_million_input_tokens'),
                data.get('usd_per_million_output_tokens'), bool(data.get('is_active')),
                data.get('notes'), model_id
            ))
            conn.commit()
            return jsonify({'success': True, 'message': 'Model updated successfully.'})
        finally:
            conn.close()
    except Exception as e:
        print(f"Error updating model: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/models/<int:model_id>/toggle', methods=['GET'])
@admin_required
def admin_toggle_model(model_id):
    conn = get_db_conn()
    try:
        model = conn.execute('SELECT is_active FROM llm_models WHERE id = ?', (model_id,)).fetchone()
        if not model:
            return jsonify({'error': 'Model not found.'}), 404
            
        new_status = not model['is_active']
        conn.execute('UPDATE llm_models SET is_active = ? WHERE id = ?', (new_status, model_id))
        conn.commit()
        action = 'enabled' if new_status else 'disabled'
        return jsonify({'success': True, 'message': f'Model successfully {action}.'})
    except Exception as e:
        print(f"Error toggling model: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/admin/models/<int:model_id>', methods=['DELETE'])
@admin_required
def admin_delete_model(model_id):
    conn = get_db_conn()
    try:
        conn.execute('DELETE FROM llm_models WHERE id = ?', (model_id,))
        conn.commit()
        return jsonify({'success': True, 'message': 'Model deleted successfully.'})
    except Exception as e:
        print(f"Error deleting model: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/model/<model_name>')
@login_required
def get_model_details(model_name):
    """Get detailed information about a specific model"""
    conn = get_db_conn()
    try:
        # Search across all model tables
        tables = ['llm_models', 'image_models', 'audio_models', 'video_models', 'models']
        model = None
        
        for table in tables:
            try:
                model = conn.execute(
                    f'SELECT * FROM {table} WHERE model_name = ? AND is_active = 1', 
                    (model_name,)
                ).fetchone()
                if model:
                    break
            except sqlite3.OperationalError:
                # Table doesn't exist, continue
                continue
        
        if not model:
            return jsonify({'error': 'Model not found'}), 404
            
        return jsonify(format_model_data(model))
        
    except Exception as e:
        print(f"Error fetching model details: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    check_db_exists()
    check_user_db_exists()
    
    # Initialize AI Client
    try:
        ai_client = AIClient(DB_PATH)
        available_models = ai_client.get_available_models()
        print(f"AI Client initialized with {len(available_models)} available models")
        if available_models:
            print("Available models:")
            for model in available_models[:5]:  # Show first 5
                print(f"  - {model['model_name']} ({model['provider_name']})")
            if len(available_models) > 5:
                print(f"  ... and {len(available_models) - 5} more")
        else:
            print("WARNING: No models available. Please check your API keys in .env file.")
    except Exception as e:
        print(f"Failed to initialize AI Client: {e}")
        print("The app will run but chat functionality will be limited.")
    
    os.makedirs('static', exist_ok=True)
    os.makedirs('db', exist_ok=True)
    
    if not os.path.exists('templates'):
        os.makedirs('templates')
        print("\nNOTE: 'templates' directory created. Please move 'index.html' into it.\n")

    app.run(debug=True, host='0.0.0.0', port=5000)