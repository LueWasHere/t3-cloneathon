# Updated app.py - Enhanced Database Integration for T3 Chat

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

# Import our AI clients
from ai_client import AIClient
from media_client import MediaClient

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
# Ensure we're using the correct absolute path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'db', 'models.db')
USER_DB_PATH = os.path.join(BASE_DIR, 'db', 'user.db')

# Initialize AI Client and Media Client
ai_client = None
media_client = None

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

def format_model_data(row, model_type='llm'):
    """Enhanced function to format database row into frontend-ready model data."""
    # Convert row to dict for easier access
    if hasattr(row, 'keys'):
        row_dict = dict(row)
    else:
        row_dict = row
    
    provider_name = row_dict['provider_name']
    model_name = row_dict['model_name']
    api_name = row_dict.get('api_name', model_name)

    # Provider mapping for logos and keys
    provider_key_map = {
        'OpenAI': 'openai',
        'Anthropic': 'claude', 
        'Google': 'gemini',
        'xAI': 'grok',
        'DeepSeek': 'deepseek',
        'Together.ai': 'meta',
        'Meta': 'meta',
        'Black Forest Labs': 'meta',
        'Cartesia': 'openai',
        'mistralai': 'meta',
        'Qwen': 'meta',
        'Nousresearch': 'meta',
        'nvidia': 'meta',
        'salesforce': 'meta',
        'Arcee AI': 'meta',
        'LG AI': 'meta',
        'Gryphe': 'meta',
        'Mixedbread AI': 'meta'
    }
    provider_key = provider_key_map.get(provider_name, provider_name.lower())
    
    # Special handling for meta models
    if provider_name in ['Together.ai', 'Meta'] and ('llama' in model_name.lower() or 'meta' in model_name.lower()):
        provider_key = 'meta'

    # Enhanced display name parsing
    main_name, sub_name = parse_model_display_name(model_name, model_type)

    # Determine premium status and icon
    is_premium = False
    premium_icon = None
    input_price = row_dict.get('usd_per_million_input_tokens')
    
    if input_price is not None and input_price > 2.5:
        is_premium = True
        if 'opus' in model_name.lower() or '405b' in model_name.lower():
            premium_icon = 'gem'
        elif row_dict.get('reasoning_enabled'):
            premium_icon = 'key'
        elif 'pro' in model_name.lower() or 'turbo' in model_name.lower() or '70b' in model_name.lower():
            premium_icon = 'flask'

    # Enhanced capabilities detection
    capabilities = get_model_capabilities(row_dict, model_name, model_type)

    # Context window formatting
    context_window = row_dict.get('context_window_max_tokens')
    context_window_formatted = None
    if context_window:
        if context_window >= 1000000:
            context_window_formatted = f"{context_window / 1000000:.1f}M"
        elif context_window >= 1000:
            context_window_formatted = f"{context_window / 1000:.0f}k"
        else:
            context_window_formatted = str(context_window)

    return {
        'model_name': model_name,
        'api_name': api_name,
        'provider_name': provider_name,
        'provider': provider_key,
        'displayNameMain': main_name,
        'displayNameSub': sub_name,
        'subtitle': row_dict.get('notes', ''),
        'premium': is_premium,
        'premium_icon': premium_icon,
        'capabilities': capabilities,
        'context_window': context_window,
        'context_window_formatted': context_window_formatted,
        'input_price': row_dict.get('usd_per_million_input_tokens'),
        'output_price': row_dict.get('usd_per_million_output_tokens'),
        'multimodal': bool(row_dict.get('multimodal_input', False)),
        'is_active': bool(row_dict.get('is_active', True))
    }

def parse_model_display_name(model_name, model_type):
    """Enhanced model name parsing for better display names."""
    main_name, sub_name = model_name, ''
    
    if model_type == 'llm':
        # GPT models
        if 'gpt-4o-mini' in model_name.lower():
            main_name, sub_name = 'GPT-4o', 'Mini'
        elif 'gpt-4o' in model_name.lower():
            main_name, sub_name = 'GPT-4o', ''
        elif 'gpt-4.1-mini' in model_name.lower():
            main_name, sub_name = 'GPT-4.1', 'Mini'
        elif 'gpt-4.1-nano' in model_name.lower():
            main_name, sub_name = 'GPT-4.1', 'Nano'
        elif 'gpt-4.1' in model_name.lower():
            main_name, sub_name = 'GPT-4.1', ''
        elif 'gpt-4.5' in model_name.lower():
            main_name, sub_name = 'GPT-4.5', 'Preview'
        
        # OpenAI o-series
        elif 'o1-pro' in model_name.lower():
            main_name, sub_name = 'o1', 'Pro'
        elif 'o1-mini' in model_name.lower():
            main_name, sub_name = 'o1', 'Mini'
        elif 'o3-mini' in model_name.lower():
            main_name, sub_name = 'o3', 'Mini'
        elif 'o4-mini' in model_name.lower():
            main_name, sub_name = 'o4', 'Mini'
        elif model_name.lower() == 'o3':
            main_name, sub_name = 'o3', ''
        
        # Claude models
        elif 'Claude Sonnet 4' in model_name:
            main_name, sub_name = 'Claude 4', 'Sonnet'
        elif 'Claude Opus 4' in model_name:
            main_name, sub_name = 'Claude 4', 'Opus'
        elif 'Claude Sonnet 3.7' in model_name:
            main_name, sub_name = 'Claude 3.7', 'Sonnet'
        elif 'Claude Sonnet 3.5' in model_name:
            main_name, sub_name = 'Claude 3.5', 'Sonnet'
        elif 'Claude 3 Opus' in model_name:
            main_name, sub_name = 'Claude 3', 'Opus'
        elif 'Claude 3 Sonnet' in model_name:
            main_name, sub_name = 'Claude 3', 'Sonnet'
        elif 'Claude 3 Haiku' in model_name:
            main_name, sub_name = 'Claude 3', 'Haiku'
        elif 'Claude Haiku 3.5' in model_name:
            main_name, sub_name = 'Claude 3.5', 'Haiku'
        
        # Gemini models
        elif 'Gemini 2.5 Flash' in model_name:
            main_name, sub_name = 'Gemini 2.5', 'Flash'
        elif 'Gemini 2.5 Pro' in model_name:
            main_name, sub_name = 'Gemini 2.5', 'Pro'
        elif 'Gemini 2.0 Flash' in model_name:
            main_name, sub_name = 'Gemini 2.0', 'Flash'
        elif 'Gemini 1.5 Pro' in model_name:
            main_name, sub_name = 'Gemini 1.5', 'Pro'
        elif 'Gemini 1.5 Flash' in model_name:
            main_name, sub_name = 'Gemini 1.5', 'Flash'
        
        # DeepSeek models
        elif 'DeepSeek-R1' in model_name:
            main_name, sub_name = 'DeepSeek', 'R1'
        elif 'deepseek-reasoner' in model_name or 'deepseek-coder' in model_name:
            main_name, sub_name = 'DeepSeek', 'Coder'
        elif 'DeepSeek-V3' in model_name:
            main_name, sub_name = 'DeepSeek', 'V3'
        
        # Llama models
        elif 'Llama-4-Scout' in model_name:
            main_name, sub_name = 'Llama 4', 'Scout'
        elif 'Llama-4-Maverick' in model_name:
            main_name, sub_name = 'Llama 4', 'Maverick'
        elif 'Llama-3.3-70B' in model_name:
            main_name, sub_name = 'Llama 3.3', '70B'
        elif 'Llama-3.2-90B' in model_name:
            main_name, sub_name = 'Llama 3.2', '90B Vision'
        elif 'Llama-3.2-11B' in model_name:
            main_name, sub_name = 'Llama 3.2', '11B Vision'
        elif 'Llama-3.2-3B' in model_name:
            main_name, sub_name = 'Llama 3.2', '3B'
        elif 'Llama-3.1-405B' in model_name:
            main_name, sub_name = 'Llama 3.1', '405B'
        elif 'Llama-3.1-70B' in model_name:
            main_name, sub_name = 'Llama 3.1', '70B'
        elif 'Llama-3.1-8B' in model_name:
            main_name, sub_name = 'Llama 3.1', '8B'
        elif 'Llama-Vision-Free' in model_name:
            main_name, sub_name = 'Llama Vision', 'Free'
        
        # Other models with generic parsing
        else:
            # Try to extract version numbers and model types
            if '/' in model_name:
                model_name = model_name.split('/')[-1]  # Take the part after the last slash
            
            # Look for patterns like ModelName-VersionNumber
            match = re.match(r'([a-zA-Z0-9\._\-]+?)[\-\s]+([\d\.]+[a-zA-Z]*(?:\-[a-zA-Z0-9]+)*)', model_name, re.IGNORECASE)
            if match and len(match.groups()) >= 2:
                base_name = match.groups()[0].replace('-', ' ').replace('_', ' ')
                version_part = match.groups()[1]
                main_name = ' '.join(word.capitalize() for word in base_name.split())
                sub_name = version_part.upper() if len(version_part) <= 5 else version_part.capitalize()
    
    elif model_type == 'image':
        if 'FLUX.1.1' in model_name and 'pro' in model_name.lower():
            main_name, sub_name = 'FLUX.1.1', 'Pro'
        elif 'FLUX.1' in model_name:
            if 'schnell' in model_name.lower():
                main_name, sub_name = 'FLUX.1', 'Schnell'
            elif 'dev' in model_name.lower():
                main_name, sub_name = 'FLUX.1', 'Dev'
            elif 'redux' in model_name.lower():
                main_name, sub_name = 'FLUX.1', 'Redux'
            elif 'depth' in model_name.lower():
                main_name, sub_name = 'FLUX.1', 'Depth'
            elif 'canny' in model_name.lower():
                main_name, sub_name = 'FLUX.1', 'Canny'
            else:
                main_name, sub_name = 'FLUX.1', ''
        elif 'Imagen 3' in model_name:
            main_name, sub_name = 'Imagen', '3'
        elif 'gpt-image-1' in model_name:
            main_name, sub_name = 'GPT Image', '1'
        elif 'Gemini 2.0 Flash' in model_name and 'Image' in model_name:
            main_name, sub_name = 'Gemini 2.0', 'Image Gen'
    
    elif model_type == 'audio':
        if 'sonic-2' in model_name.lower():
            main_name, sub_name = 'Sonic', '2'
        elif 'sonic' in model_name.lower():
            main_name, sub_name = 'Sonic', '1'
        elif 'gpt-4o-audio' in model_name:
            main_name, sub_name = 'GPT-4o', 'Audio'
        elif 'gpt-4o-mini-audio' in model_name:
            main_name, sub_name = 'GPT-4o Mini', 'Audio'
        elif 'gpt-4o-realtime' in model_name:
            main_name, sub_name = 'GPT-4o', 'Realtime'
        elif 'gpt-4o-mini-realtime' in model_name:
            main_name, sub_name = 'GPT-4o Mini', 'Realtime'
        elif 'Gemini 2.5' in model_name and 'TTS' in model_name:
            main_name, sub_name = 'Gemini 2.5', 'TTS'
        elif 'Gemini 2.5' in model_name and 'Audio' in model_name:
            main_name, sub_name = 'Gemini 2.5', 'Audio'
        elif 'Gemini 2.0 Flash Live' in model_name:
            main_name, sub_name = 'Gemini 2.0', 'Live'
    
    elif model_type == 'video':
        if 'Veo 2' in model_name:
            main_name, sub_name = 'Veo', '2'

    return main_name, sub_name

def get_model_capabilities(row, model_name, model_type):
    """Enhanced capability detection based on database fields and model characteristics."""
    # Convert row to dict for easier access if needed
    if hasattr(row, 'keys') and not isinstance(row, dict):
        row_dict = dict(row)
    else:
        row_dict = row
        
    capabilities = {
        'vision': bool(row_dict.get('supports_images_input', False)),
        'reasoning': bool(row_dict.get('reasoning_enabled', False)),
        'coding': False,
        'web': False,
        'docs': bool(row_dict.get('supports_pdfs_input', False)),
    }
    
    # Enhanced coding detection
    coding_indicators = ['coder', 'codex', 'code', 'programming', 'dev']
    if any(indicator in model_name.lower() for indicator in coding_indicators):
        capabilities['coding'] = True
    
    # Enhanced web search detection
    web_indicators = ['search', 'web', 'browse', 'grok']
    if any(indicator in model_name.lower() for indicator in web_indicators):
        capabilities['web'] = True
    
    # Special cases for specific providers
    provider_name = row_dict.get('provider_name', '')
    if provider_name.lower() == 'xai':
        capabilities['web'] = True  # Grok models typically have web access
    
    return capabilities

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
        media_type = data.get('mediaType', 'llm')
        
        if not message: 
            return jsonify({'error': 'Empty message'}), 400
        
        # Handle different media types
        if media_type == 'image':
            if not media_client:
                return jsonify({'error': 'Media client not initialized. Please check your API keys.'}), 500
            
            try:
                result = media_client.generate_image(model, message)
                if isinstance(result, str):  # Error message
                    return jsonify({'error': result}), 500
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': f'Image generation failed: {str(e)}'}), 500
        
        elif media_type == 'video':
            if not media_client:
                return jsonify({'error': 'Media client not initialized. Please check your API keys.'}), 500
            
            try:
                result = media_client.generate_video(model, message)
                if isinstance(result, str):  # Error message
                    return jsonify({'error': result}), 500
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': f'Video generation failed: {str(e)}'}), 500
        
        else:  # Default to LLM (text)
            if not ai_client:
                return jsonify({'error': 'AI client not initialized. Please check your API keys.'}), 500
            
            try:
                response = ai_client.generate_response(model, message)
                return jsonify({'response': response, 'type': 'text'})
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
            except Exception as e:
                print(f"AI API Error: {e}")
                return jsonify({'error': f'Sorry, I encountered an error while processing your request. Please try again or select a different model.'}), 500
            
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/models/categorized')
@login_required
def get_categorized_models():
    """Enhanced endpoint to fetch all categorized models from the database with full model information."""
    conn = get_db_conn()
    try:
        categorized_models = {
            'llm_models': [],
            'image_models': [],
            'audio_models': [],
            'video_models': []
        }
        
        # Define tables and their corresponding keys
        table_configs = [
            ('llm_models', 'llm_models'),
            ('image_models', 'image_models'),
            ('audio_models', 'audio_models'),
            ('video_models', 'video_models')
        ]
        
        for table_name, key in table_configs:
            try:
                # Check if table exists
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
                    (table_name,)
                )
                if not cursor.fetchone():
                    print(f"Table {table_name} doesn't exist, skipping...")
                    continue
                
                # Fetch models from table with enhanced ordering
                query = f'''
                    SELECT * FROM {table_name} 
                    WHERE is_active = 1 
                    ORDER BY 
                        CASE provider_name 
                            WHEN 'Anthropic' THEN 1
                            WHEN 'Google' THEN 2
                            WHEN 'OpenAI' THEN 3
                            WHEN 'DeepSeek' THEN 4
                            WHEN 'Meta' THEN 5
                            WHEN 'xAI' THEN 6
                            ELSE 7
                        END,
                        COALESCE(usd_per_million_input_tokens, 0) DESC,
                        model_name
                '''
                
                models = conn.execute(query).fetchall()
                
                # Format each model with enhanced data
                model_type = table_name.replace('_models', '')
                formatted_models = []
                for model in models:
                    try:
                        formatted_model = format_model_data(model, model_type)
                        formatted_models.append(formatted_model)
                    except Exception as e:
                        model_name = model['model_name'] if 'model_name' in model.keys() else 'unknown'
                        print(f"Error formatting model {model_name}: {e}")
                        continue
                
                categorized_models[key] = formatted_models
                print(f"Loaded {len(formatted_models)} models from {table_name}")
                
            except sqlite3.OperationalError as e:
                print(f"Error querying {table_name}: {e}")
                continue
        
        # Log summary
        total_models = sum(len(models) for models in categorized_models.values())
        print(f"Total models loaded: {total_models}")
        
        return jsonify(categorized_models)
        
    except Exception as e:
        print(f"Error in get_categorized_models: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/models')
@login_required
def get_models_data():
    """Enhanced endpoint to fetch LLM models with better categorization."""
    conn = get_db_conn()
    try:
        # Enhanced query with better ordering
        db_models = conn.execute('''
            SELECT * FROM llm_models 
            WHERE is_active = 1 
            ORDER BY 
                CASE provider_name 
                    WHEN 'Anthropic' THEN 1
                    WHEN 'Google' THEN 2
                    WHEN 'OpenAI' THEN 3
                    WHEN 'DeepSeek' THEN 4
                    WHEN 'Meta' THEN 5
                    WHEN 'xAI' THEN 6
                    ELSE 7
                END,
                COALESCE(usd_per_million_input_tokens, 0) DESC,
                model_name
        ''').fetchall()
        
    except sqlite3.OperationalError as e:
        print(f"Error querying database: {e}")
        return jsonify({'error': f"Database query failed: {e}"}), 500
    finally:
        conn.close()

    # Enhanced popular model detection
    popular_model_patterns = [
        'Claude Sonnet 4', 'Claude Opus 4', 'Gemini 2.5', 'Gemini 2.0 Flash', 
        'gpt-4o', 'o3-mini', 'o1-mini', 'DeepSeek-R1', 'Llama-4', 'grok'
    ]
    
    popular_models = []
    all_other_models = []

    for row in db_models:
        # Convert row to dict for easier access
        row_dict = dict(row) if hasattr(row, 'keys') else row
        
        formatted = format_model_data(row, 'llm')
        
        # Check if model matches popular patterns
        is_popular = any(
            pattern.lower() in row_dict['model_name'].lower() 
            for pattern in popular_model_patterns
        )
        
        # Also consider high-end models as popular (expensive or reasoning-enabled)
        if not is_popular:
            input_price = row_dict.get('usd_per_million_input_tokens', 0)
            is_reasoning = row_dict.get('reasoning_enabled', False)
            if input_price and input_price > 5.0:  # High-end models
                is_popular = True
            elif is_reasoning:  # Reasoning models
                is_popular = True
        
        if is_popular and len(popular_models) < 12:  # Limit popular models
            popular_models.append(formatted)
        else:
            all_other_models.append(formatted)
    
    # If still not enough popular models, take from the beginning
    while len(popular_models) < min(8, len(popular_models) + len(all_other_models)):
        if all_other_models:
            popular_models.append(all_other_models.pop(0))
        else:
            break

    return jsonify({
        'popular': popular_models,
        'all': all_other_models,
    })

@app.route('/models/available')
@login_required
def get_available_models():
    """Get models that have working API clients with enhanced information."""
    if not ai_client:
        return jsonify({'available': []})
    
    available = ai_client.get_available_models()
    
    # Enhance available models with database information
    enhanced_available = []
    conn = get_db_conn()
    try:
        for model in available:
            try:
                # Get full model info from database
                table = model.get('table', 'llm_models')
                model_row = conn.execute(
                    f'SELECT * FROM {table} WHERE model_name = ? AND is_active = 1',
                    (model['model_name'],)
                ).fetchone()
                
                if model_row:
                    model_type = table.replace('_models', '') if '_models' in table else 'llm'
                    enhanced_model = format_model_data(model_row, model_type)
                    enhanced_model['table'] = table
                    enhanced_available.append(enhanced_model)
                else:
                    enhanced_available.append(model)
            except Exception as e:
                print(f"Error enhancing model {model.get('model_name', 'unknown')}: {e}")
                enhanced_available.append(model)
    finally:
        conn.close()
    
    return jsonify({'available': enhanced_available})

# --- Admin Routes ---
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
    """Get detailed information about a specific model with enhanced data."""
    conn = get_db_conn()
    try:
        # Search across all model tables
        tables = ['llm_models', 'image_models', 'audio_models', 'video_models', 'models']
        model = None
        model_type = 'llm'
        
        for table in tables:
            try:
                model = conn.execute(
                    f'SELECT * FROM {table} WHERE model_name = ? AND is_active = 1', 
                    (model_name,)
                ).fetchone()
                if model:
                    model_type = table.replace('_models', '') if '_models' in table else 'llm'
                    break
            except sqlite3.OperationalError:
                continue
        
        if not model:
            return jsonify({'error': 'Model not found'}), 404
            
        formatted_model = format_model_data(model, model_type)
        return jsonify(formatted_model)
        
    except Exception as e:
        print(f"Error fetching model details: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    print(f"Starting T3 Chat with database at: {DB_PATH}")
    check_db_exists()
    check_user_db_exists()
    
    # Initialize AI Client
    try:
        ai_client = AIClient(DB_PATH)
        available_models = ai_client.get_available_models()
        print(f"AI Client initialized with {len(available_models)} available models")
        if available_models:
            print("Available LLM models:")
            llm_models = [m for m in available_models if m.get('table') == 'llm_models'][:5]
            for model in llm_models:
                print(f"  - {model['model_name']} ({model['provider_name']})")
            if len([m for m in available_models if m.get('table') == 'llm_models']) > 5:
                llm_count = len([m for m in available_models if m.get('table') == 'llm_models'])
                print(f"  ... and {llm_count - 5} more LLM models")
        else:
            print("WARNING: No LLM models available. Please check your API keys in .env file.")
    except Exception as e:
        print(f"Failed to initialize AI Client: {e}")
        print("The app will run but LLM chat functionality will be limited.")
    
    # Initialize Media Client
    try:
        media_client = MediaClient(DB_PATH)
        available_image_models = media_client.get_available_models('image')
        available_video_models = media_client.get_available_models('video')
        available_audio_models = media_client.get_available_models('audio')
        
        total_media_models = len(available_image_models) + len(available_video_models) + len(available_audio_models)
        print(f"Media Client initialized with {total_media_models} available media models")
        print(f"  - {len(available_image_models)} image models")
        print(f"  - {len(available_video_models)} video models")
        print(f"  - {len(available_audio_models)} audio models")
        
        if total_media_models == 0:
            print("WARNING: No media models available. Please check your API keys in .env file.")
    except Exception as e:
        print(f"Failed to initialize Media Client: {e}")
        print("The app will run but image/video/audio generation will be limited.")
    
    os.makedirs('static', exist_ok=True)
    os.makedirs('db', exist_ok=True)
    
    if not os.path.exists('templates'):
        os.makedirs('templates')
        print("\nNOTE: 'templates' directory created. Please move your HTML files into it.\n")

    app.run(debug=True, host='0.0.0.0', port=5000)