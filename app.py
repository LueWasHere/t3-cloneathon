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

# --- Load Environment Variables ---
# This will load the ADMIN_EMAIL from your .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# --- Optional: Customize the "Remember Me" duration ---
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)
# --- Database Configuration ---
DB_DIR = 'db'
DB_PATH = os.path.join(DB_DIR, 'models.db')
USER_DB_PATH = os.path.join(DB_DIR, 'user.db')

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

# --- End Database ---

# --- Authentication Setup ---
# Import the User class and auth blueprint from our new auth.py
from auth import auth as auth_blueprint, User

app.register_blueprint(auth_blueprint)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Redirect to this page if user is not logged in
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # This function reloads the user object from the user ID stored in the session
    return User.get(user_id)
# --- End Authentication ---

# --- NEW: Admin Authorization Decorator ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
        if not ADMIN_EMAIL:
            print("WARNING: ADMIN_EMAIL not set in .env file. Admin panel is disabled.")
            abort(404) # Not found, as the admin panel effectively doesn't exist
            
        if not current_user.is_authenticated:
            return login_manager.unauthorized()
            
        if current_user.email != ADMIN_EMAIL:
            abort(403) # Forbidden
            
        return f(*args, **kwargs)
    return decorated_function

# Add this new route anywhere in your app.py file, for example, after the index route.
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
        # Ensure value is an integer before formatting
        return f'{int(value):,}'
    except (ValueError, TypeError):
        return str(value)

# Register the custom filter with the Jinja environment
app.jinja_env.filters['numberformat'] = format_number_with_comma


# --- Find and replace your entire '/settings' route with this new version ---

@app.route('/settings')
@login_required
def settings():
    """Renders the user settings page with dynamic token usage data."""
    
    # Define the total token limit for the user's plan.
    total_tokens = 10000  # New limit is 10,000 tokens

    # 1. Fetch the user's token usage from the database
    conn = get_user_db_conn()
    user_data = conn.execute(
        'SELECT token_quota FROM user_accounts WHERE user_id = ?',
        (current_user.id,)
    ).fetchone()
    conn.close()

    # 2. Get the number of tokens used, defaulting to 0 if NULL
    tokens_used = 0
    if user_data and user_data['token_quota'] is not None:
        tokens_used = int(user_data['token_quota'])

    # 3. Calculate remaining tokens and progress bar percentage
    tokens_remaining = total_tokens - tokens_used
    # Ensure remaining tokens doesn't display as a negative number
    if tokens_remaining < 0:
        tokens_remaining = 0
        
    progress_percentage = 0
    if total_tokens > 0:
        # Calculate the percentage and ensure it doesn't exceed 100%
        progress_percentage = min(100, (tokens_used / total_tokens) * 100)

    # 4. Pass all the calculated token data to the template
    return render_template(
        'settings.html',
        tokens_used=tokens_used,
        total_tokens=total_tokens,
        tokens_remaining=tokens_remaining,
        progress_percentage=progress_percentage
    )

def get_ai_response(message, model_name):
    """Simulate AI response based on the selected model"""
    time.sleep(random.uniform(0.5, 1.5))
    message_lower = message.lower()
    
    # Get model info from database for more realistic responses
    conn = get_db_conn()
    try:
        model_info = conn.execute(
            'SELECT provider_name, reasoning_enabled, supports_images_input FROM models WHERE model_name = ? AND is_active = 1', 
            (model_name,)
        ).fetchone()
        
        if model_info:
            provider = model_info['provider_name']
            has_reasoning = model_info['reasoning_enabled']
            has_vision = model_info['supports_images_input']
        else:
            provider = "Unknown"
            has_reasoning = False
            has_vision = False
    finally:
        conn.close()
    
    # Generate responses based on model capabilities
    if 'hello' in message_lower or 'hi' in message_lower:
        if has_reasoning:
            return f"Hello! I'm {model_name} from {provider}. I'm equipped with advanced reasoning capabilities to help you with complex problems. What would you like to explore?"
        elif has_vision:
            return f"Hi there! I'm {model_name} from {provider}. I can help with text and analyze images too. How can I assist you today?"
        else:
            return f"Hello! I'm {model_name} from {provider}. How can I help you today?"
    
    elif 'how does ai work' in message_lower:
        if has_reasoning:
            return f"AI works through complex neural networks that process patterns in data. As {model_name}, I use advanced reasoning capabilities to understand relationships and solve multi-step problems systematically.\n\n*Response generated by {model_name} ({provider})*"
        else:
            return f"AI works by using algorithms to find patterns in data. This allows it to make predictions and generate new content. It's a broad field, but that's the core idea!\n\n*Response generated by {model_name} ({provider})*"
    
    elif 'black holes' in message_lower:
        return f"Yes, black holes are definitely real! They are regions in space where gravity is so strong that nothing, not even light, can escape. They're predicted by Einstein's theory of general relativity and we've even captured images of them!\n\n*Response generated by {model_name} ({provider})*"
    
    elif 'strawberry' in message_lower and ('r' in message_lower or 'letter' in message_lower):
        if has_reasoning:
            return f"Let me carefully analyze the word 'strawberry' letter by letter: s-t-r-a-w-b-e-r-r-y. I can identify the letter 'r' appears 3 times: once in position 3, once in position 8, and once in position 9.\n\n*Response generated by {model_name} ({provider}) with reasoning*"
        else:
            return f"There are three 'r's in the word 'strawberry'.\n\n*Response generated by {model_name} ({provider})*"
    
    elif 'meaning of life' in message_lower:
        if has_reasoning:
            return f"This is a profound philosophical question that has been contemplated for millennia. From my reasoning perspective, meaning often emerges through: purpose-driven action, meaningful relationships, personal growth, and contributing to something larger than ourselves. Different philosophical traditions offer various frameworks - existentialists emphasize creating your own meaning, while others find it through spirituality, service, or knowledge.\n\n*Response generated by {model_name} ({provider}) with reasoning*"
        else:
            return f"That's a deep question! There's no single answer, but many find meaning in relationships, personal growth, and contributing to something bigger than themselves.\n\n*Response generated by {model_name} ({provider})*"
    
    else:
        capabilities = []
        if has_reasoning: capabilities.append("advanced reasoning")
        if has_vision: capabilities.append("vision analysis")
        
        cap_text = f" with {' and '.join(capabilities)}" if capabilities else ""
        return f"That's an interesting question! As {model_name} from {provider}{cap_text}, I'm processing your request. In a real application, I would provide a detailed answer here."


def format_model_data(row):
    """Formats a database row into a dictionary for the frontend."""
    provider_name = row['provider_name']
    model_name = row['model_name']

    # Map provider names to frontend keys
    provider_key_map = {
        'OpenAI': 'openai',
        'Anthropic': 'claude',
        'Google': 'gemini',
        'xAI': 'grok',
        'DeepSeek': 'deepseek',
        'Together.ai': 'meta',  # For Llama models
        'Meta': 'meta'
    }
    provider_key = provider_key_map.get(provider_name, provider_name.lower())
    
    # Special handling for Llama models on Together.ai
    if provider_name == 'Together.ai' and 'meta-llama' in model_name:
        provider_key = 'meta'

    # Create user-friendly display names
    main_name, sub_name = model_name, ''
    
    # Parse model names for better display
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
        # Fallback parsing
        match = re.match(r'([a-zA-Z0-9\._/]+-?)([\d\.]+[a-zA-Z]*-?instruct|[\d\.]+-?pro|[\d\.]+-?flash|[\d\.]+-?sonnet|[\d\.]+-?opus|[\d\.]+-?haiku|o-?mini|turbo|mini)?', model_name, re.IGNORECASE)
        if match and match.groups()[1]:
            main_name_raw = match.groups()[0].strip('-').replace('meta-llama/Llama', 'Llama').replace('claude-','Claude ')
            sub_name_raw = match.groups()[1].strip('-').replace('-Instruct', '')
            main_name = ' '.join(p.capitalize() for p in main_name_raw.replace('-', ' ').split())
            sub_name = ' '.join(p.capitalize() for p in sub_name_raw.replace('-', ' ').split())

    # Determine if model is premium based on pricing
    is_premium = False
    premium_icon = None
    input_price = row['usd_per_million_input_tokens']
    
    if input_price is not None and input_price > 2.5:  # Premium threshold
        is_premium = True
        
        # Assign premium icons based on model characteristics
        if 'opus' in model_name.lower() or '405b' in model_name.lower():
            premium_icon = 'gem'  # Top-tier models
        elif row['reasoning_enabled']:
            premium_icon = 'key'  # Reasoning models
        elif 'pro' in model_name.lower() or 'turbo' in model_name.lower() or '70b' in model_name.lower():
            premium_icon = 'flask'  # Advanced models

    # Map capabilities from database columns
    capabilities = {
        'vision': bool(row['supports_images_input']),
        'reasoning': bool(row['reasoning_enabled']),
        'coding': 'coder' in model_name.lower() or 'codex' in model_name.lower(),
        'web': provider_name.lower() == 'xai',  # Grok models have web access
        'docs': bool(row['supports_pdfs_input']),
    }

    return {
        'name': model_name,
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
@login_required # This route is now protected
def index():
    # The `current_user` object is automatically available in templates
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    # Added auth.css to be served
    if filename == 'auth.css':
        return send_from_directory('static', 'auth.css')
    return send_from_directory('static', filename)

@app.route('/chat', methods=['POST'])
@login_required # Protect the chat API endpoint
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        model = data.get('model', 'gpt-4o-mini')
        
        if not message: 
            return jsonify({'error': 'Empty message'}), 400
            
        response = get_ai_response(message, model)
        return jsonify({'response': response})
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/models')
@login_required # Protect the models API endpoint
def get_models_data():
    """Fetch all active models from the database"""
    conn = get_db_conn()
    try:
        # Query all active models, ordered by provider and price
        db_models = conn.execute('''
            SELECT * FROM models 
            WHERE is_active = 1 
            ORDER BY provider_name, usd_per_million_input_tokens DESC
        ''').fetchall()
        
    except sqlite3.OperationalError as e:
        print(f"Error querying database: {e}")
        return jsonify({'error': f"Database query failed: {e}. Is the DB schema correct?"}), 500
    finally:
        conn.close()

    # Define popular models (these will be featured)
    popular_model_names = ['gpt-4o', 'claude-3.5-sonnet-20240620', 'gemini-1.5-pro']
    
    popular_models = []
    all_other_models = []

    # Categorize models
    for row in db_models:
        formatted = format_model_data(row)
        if row['model_name'] in popular_model_names:
            popular_models.append(formatted)
        else:
            all_other_models.append(formatted)
    
    # Sort popular models by their predefined order
    popular_models.sort(key=lambda m: popular_model_names.index(m['name']))

    return jsonify({
        'popular': popular_models,
        'all': all_other_models,
    })

# --- Admin Routes (Now protected by @admin_required) ---

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard for managing models"""
    return render_template('admin.html')

@app.route('/admin/models')
@admin_required
def admin_get_models():
    """Get all models with full details for admin interface"""
    conn = get_db_conn()
    try:
        # Get all models (including inactive ones)
        models = conn.execute('''
            SELECT * FROM models 
            ORDER BY provider_name, model_name
        ''').fetchall()
        
        # Convert to list of dictionaries for JSON response
        models_list = []
        for model in models:
            model_dict = {}
            for key in model.keys():
                model_dict[key] = model[key]
            models_list.append(model_dict)
        
        return jsonify({'models': models_list})
        
    except Exception as e:
        print(f"Error fetching models for admin: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/admin/models', methods=['POST'])
@admin_required
def admin_add_model():
    """Add a new model"""
    try:
        data = request.get_json()
        
        # Required fields
        provider_name = data.get('provider_name', '').strip()
        model_name = data.get('model_name', '').strip()
        
        if not provider_name or not model_name:
            return jsonify({'error': 'Provider name and model name are required'}), 400
        
        conn = get_db_conn()
        try:
            # Check if model already exists
            existing = conn.execute(
                'SELECT id FROM models WHERE model_name = ?', 
                (model_name,)
            ).fetchone()
            
            if existing:
                return jsonify({'error': f'Model {model_name} already exists'}), 400
            
            # Insert new model
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO models (
                    provider_name, model_name, context_window_max_tokens,
                    supports_images_input, supports_pdfs_input, multimodal_input,
                    reasoning_enabled, usd_per_million_input_tokens, 
                    usd_per_million_output_tokens, is_active, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                provider_name,
                model_name,
                data.get('context_window_max_tokens'),
                bool(data.get('supports_images_input', False)),
                bool(data.get('supports_pdfs_input', False)),
                bool(data.get('multimodal_input', False)),
                bool(data.get('reasoning_enabled', False)),
                data.get('usd_per_million_input_tokens'),
                data.get('usd_per_million_output_tokens'),
                bool(data.get('is_active', True)),
                data.get('notes', '')
            ))
            
            conn.commit()
            new_id = cursor.lastrowid
            
            return jsonify({
                'success': True, 
                'message': f'Model {model_name} added successfully',
                'id': new_id
            })
            
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Error adding model: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/models/<int:model_id>', methods=['PUT'])
@admin_required
def admin_update_model(model_id):
    """Update an existing model"""
    try:
        data = request.get_json()
        
        conn = get_db_conn()
        try:
            # Check if model exists
            existing = conn.execute(
                'SELECT id FROM models WHERE id = ?', 
                (model_id,)
            ).fetchone()
            
            if not existing:
                return jsonify({'error': f'Model with ID {model_id} not found'}), 404
            
            # Update model
            conn.execute('''
                UPDATE models SET
                    provider_name = ?,
                    model_name = ?,
                    context_window_max_tokens = ?,
                    supports_images_input = ?,
                    supports_pdfs_input = ?,
                    multimodal_input = ?,
                    reasoning_enabled = ?,
                    usd_per_million_input_tokens = ?,
                    usd_per_million_output_tokens = ?,
                    is_active = ?,
                    notes = ?
                WHERE id = ?
            ''', (
                data.get('provider_name', ''),
                data.get('model_name', ''),
                data.get('context_window_max_tokens'),
                bool(data.get('supports_images_input', False)),
                bool(data.get('supports_pdfs_input', False)),
                bool(data.get('multimodal_input', False)),
                bool(data.get('reasoning_enabled', False)),
                data.get('usd_per_million_input_tokens'),
                data.get('usd_per_million_output_tokens'),
                bool(data.get('is_active', True)),
                data.get('notes', ''),
                model_id
            ))
            
            conn.commit()
            
            return jsonify({
                'success': True, 
                'message': f'Model updated successfully'
            })
            
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Error updating model: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/models/<int:model_id>', methods=['DELETE'])
@admin_required
def admin_delete_model(model_id):
    """Delete a model"""
    try:
        conn = get_db_conn()
        try:
            # Check if model exists
            existing = conn.execute(
                'SELECT model_name FROM models WHERE id = ?', 
                (model_id,)
            ).fetchone()
            
            if not existing:
                return jsonify({'error': f'Model with ID {model_id} not found'}), 404
            
            model_name = existing['model_name']
            
            # Delete model
            conn.execute('DELETE FROM models WHERE id = ?', (model_id,))
            conn.commit()
            
            return jsonify({
                'success': True, 
                'message': f'Model {model_name} deleted successfully'
            })
            
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Error deleting model: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/models/<int:model_id>/toggle')
@admin_required
def admin_toggle_model(model_id):
    """Toggle model active status"""
    try:
        conn = get_db_conn()
        try:
            # Get current status
            existing = conn.execute(
                'SELECT model_name, is_active FROM models WHERE id = ?', 
                (model_id,)
            ).fetchone()
            
            if not existing:
                return jsonify({'error': f'Model with ID {model_id} not found'}), 404
            
            model_name = existing['model_name']
            new_status = not bool(existing['is_active'])
            
            # Toggle status
            conn.execute(
                'UPDATE models SET is_active = ? WHERE id = ?', 
                (new_status, model_id)
            )
            conn.commit()
            
            status_text = "activated" if new_status else "deactivated"
            
            return jsonify({
                'success': True, 
                'message': f'Model {model_name} {status_text}',
                'is_active': new_status
            })
            
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Error toggling model: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/providers')
@admin_required
def admin_get_providers():
    """Get list of all providers"""
    conn = get_db_conn()
    try:
        providers = conn.execute('''
            SELECT provider_name, COUNT(*) as model_count,
                   SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_count
            FROM models 
            GROUP BY provider_name
            ORDER BY provider_name
        ''').fetchall()
        
        provider_list = []
        for provider in providers:
            provider_list.append({
                'name': provider['provider_name'],
                'total_models': provider['model_count'],
                'active_models': provider['active_count']
            })
        
        return jsonify({'providers': provider_list})
        
    except Exception as e:
        print(f"Error fetching providers: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/admin/search')
@admin_required
def admin_search_models():
    """Search models by name, provider, or notes"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'models': []})
    
    conn = get_db_conn()
    try:
        search_pattern = f'%{query}%'
        models = conn.execute('''
            SELECT * FROM models 
            WHERE model_name LIKE ? 
               OR provider_name LIKE ? 
               OR notes LIKE ?
            ORDER BY is_active DESC, provider_name, model_name
        ''', (search_pattern, search_pattern, search_pattern)).fetchall()
        
        models_list = []
        for model in models:
            model_dict = {}
            for key in model.keys():
                model_dict[key] = model[key]
            models_list.append(model_dict)
        
        return jsonify({'models': models_list})
        
    except Exception as e:
        print(f"Error searching models: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/model/<model_name>')
@login_required
def get_model_details(model_name):
    """Get detailed information about a specific model"""
    conn = get_db_conn()
    try:
        model = conn.execute(
            'SELECT * FROM models WHERE model_name = ? AND is_active = 1', 
            (model_name,)
        ).fetchone()
        
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
    check_user_db_exists() # Add this check for the new database
    
    # Create directories if they don't exist
    os.makedirs('static', exist_ok=True)
    os.makedirs('db', exist_ok=True)
    
    if not os.path.exists('templates'):
        os.makedirs('templates')
        print("\nNOTE: 'templates' directory created. Please move 'index.html' into it.\n")

    app.run(debug=True, host='0.0.0.0', port=5000)