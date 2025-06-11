# ai_client.py - Fixed AI API Integration with Better Model Mapping

import os
import sqlite3
from dotenv import load_dotenv
import logging

# Import provider-specific libraries
try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import requests
except ImportError:
    requests = None

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIClient:
    def __init__(self, db_path):
        self.db_path = db_path
        self._setup_clients()
        self._create_model_mapping()
    
    def _setup_clients(self):
        """Initialize API clients for different providers"""
        self.clients = {}
        
        # OpenAI
        if openai and os.getenv("OPENAI_API_KEY"):
            self.clients['openai'] = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            logger.info("OpenAI client initialized")
        
        # Anthropic
        if anthropic and os.getenv("ANTHROPIC_API_KEY"):
            self.clients['anthropic'] = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            logger.info("Anthropic client initialized")
        
        # Google
        if genai and os.getenv("GOOGLE_API_KEY"):
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.clients['google'] = genai
            logger.info("Google AI client initialized")
        
        # DeepSeek (uses OpenAI-compatible API)
        if openai and os.getenv("DEEPSEEK_API_KEY"):
            self.clients['deepseek'] = openai.OpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com/v1"
            )
            logger.info("DeepSeek client initialized")
        
        # Together.ai (for Meta/Llama models)
        if openai and os.getenv("TOGETHER_API_KEY"):
            self.clients['together'] = openai.OpenAI(
                api_key=os.getenv("TOGETHER_API_KEY"),
                base_url="https://api.together.xyz/v1"
            )
            logger.info("Together.ai client initialized")
    
    def _create_model_mapping(self):
        """Create mapping from frontend display names to database model names"""
        self.display_name_mapping = {
            # Google/Gemini models
            'Gemini 2.5 Flash': 'Gemini 2.5 Flash Preview 05-20',
            'Gemini 2.5 Pro': 'Gemini 2.5 Pro Preview',
            'Gemini 2.0 Flash': 'Gemini 2.0 Flash',
            'Gemini 1.5 Flash': 'Gemini 1.5 Flash',
            'Gemini 1.5 Pro': 'Gemini 1.5 Pro',
            
            # Anthropic/Claude models
            'Claude 4 Sonnet': 'Claude Sonnet 4',
            'Claude Sonnet 4': 'Claude Sonnet 4',
            'Claude 3.5 Sonnet': 'Claude Sonnet 3.5',
            'Claude 3 Opus': 'Claude 3 Opus',
            'Claude 3 Haiku': 'Claude 3 Haiku',
            
            # OpenAI models
            'GPT-4o': 'gpt-4o',
            'GPT-4o Mini': 'gpt-4o-mini',
            'o1-mini': 'o1-mini',
            'o3-mini': 'o3-mini',
            
            # DeepSeek models
            'DeepSeek R1': 'DeepSeek-R1',
            'DeepSeek Coder': 'deepseek-reasoner',
            'DeepSeek Coder V2': 'deepseek-reasoner',
            
            # Meta/Llama models
            'Llama 4 Scout': 'Llama-4-Scout-17B-16E-Instruct',
            'Llama 3.1 70B': 'Llama-3.1-70B-Instruct-Turbo',
            
            # Default fallback
            'Gemini 2.5 Flash': 'Gemini 2.0 Flash',  # Fallback if 2.5 not available
        }
    
    def _resolve_model_name(self, frontend_model_name):
        """Resolve frontend model name to database model name"""
        # First try direct mapping
        if frontend_model_name in self.display_name_mapping:
            db_model_name = self.display_name_mapping[frontend_model_name]
        else:
            db_model_name = frontend_model_name
        
        # Check if the model exists in database
        model_info = self._get_model_info(db_model_name)
        if model_info:
            return db_model_name
        
        # Try fuzzy matching for partial names
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            # Try pattern matching
            model_info = conn.execute(
                'SELECT * FROM llm_models WHERE model_name LIKE ? AND is_active = 1 LIMIT 1', 
                (f'%{frontend_model_name}%',)
            ).fetchone()
            
            if model_info:
                conn.close()
                return model_info['model_name']
            
            # Try case-insensitive exact match
            model_info = conn.execute(
                'SELECT * FROM llm_models WHERE LOWER(model_name) = LOWER(?) AND is_active = 1 LIMIT 1', 
                (frontend_model_name,)
            ).fetchone()
            
            conn.close()
            
            if model_info:
                return model_info['model_name']
                
        except Exception as e:
            logger.error(f"Error resolving model name: {e}")
        
        # Return original name if no resolution found
        return frontend_model_name
    
    def _get_model_info(self, model_name):
        """Get model information from database - searches across all model tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            # Check all model tables
            tables = ['llm_models', 'image_models', 'audio_models', 'video_models']
            
            for table in tables:
                try:
                    model_info = conn.execute(
                        f'SELECT * FROM {table} WHERE model_name = ? AND is_active = 1', 
                        (model_name,)
                    ).fetchone()
                    
                    if model_info:
                        conn.close()
                        return dict(model_info)
                        
                except sqlite3.OperationalError:
                    # Table doesn't exist, continue to next
                    continue
            
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return None
    
    def _call_openai_api(self, client, model_name, message, max_tokens=1000):
        """Call OpenAI or OpenAI-compatible APIs"""
        try:
            # Use the api_name if available, otherwise use model_name
            model_info = self._get_model_info(model_name)
            api_name = model_info.get('api_name') if model_info else model_name
            
            response = client.chat.completions.create(
                model=api_name,
                messages=[{"role": "user", "content": message}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def _call_anthropic_api(self, client, model_name, message, max_tokens=1000):
        """Call Anthropic Claude API"""
        try:
            # Use the api_name if available, otherwise use model_name
            model_info = self._get_model_info(model_name)
            api_name = model_info.get('api_name') if model_info else model_name
            
            response = client.messages.create(
                model=api_name,
                messages=[{"role": "user", "content": message}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    def _call_google_api(self, genai_module, model_name, message):
        """Call Google Gemini API"""
        try:
            # Use the api_name if available, otherwise use model_name
            model_info = self._get_model_info(model_name)
            api_name = model_info.get('api_name') if model_info else model_name
            
            model = genai_module.GenerativeModel(api_name)
            response = model.generate_content(message)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Google API error: {e}")
            raise
    
    def _get_provider_key(self, provider_name):
        """Map provider names to client keys"""
        provider_map = {
            'OpenAI': 'openai',
            'Anthropic': 'anthropic', 
            'Google': 'google',
            'DeepSeek': 'deepseek',
            'Together.ai': 'together',
            'Meta': 'together',  # Meta models via Together.ai
            'xAI': 'openai',  # If xAI uses OpenAI-compatible API
            'Together': 'together',  # Handle "Together" provider name
            'mistralai': 'together',  # Mistral via Together.ai
            'Qwen': 'together',  # Qwen via Together.ai
            'Nousresearch': 'together',  # Nous via Together.ai
            'nvidia': 'together',  # Nvidia via Together.ai
            'salesforce': 'together',  # Salesforce via Together.ai
            'Arcee AI': 'together',  # Arcee via Together.ai
            'BAAI': 'together',  # BAAI via Together.ai
            'Intfloat': 'together',  # Intfloat via Together.ai
            'Mixedbread AI': 'together',  # Mixedbread via Together.ai
            'Refuel AI': 'together',  # Refuel via Together.ai
            'WhereIsAI': 'together',  # WhereIsAI via Together.ai
            'LG AI': 'together',  # LG AI via Together.ai
            'Gryphe': 'together',  # Gryphe via Together.ai
            'Alibaba Nlp': 'together',  # Alibaba via Together.ai
            'Black Forest Labs': 'together',  # Black Forest Labs via Together.ai
        }
        return provider_map.get(provider_name, provider_name.lower())
    
    def generate_response(self, frontend_model_name, message, max_tokens=1000):
        """
        Generate a response using the specified model
        
        Args:
            frontend_model_name: The display name of the model from frontend
            message: The user's message
            max_tokens: Maximum tokens in response
            
        Returns:
            str: The AI's response
        """
        # Resolve frontend model name to database model name
        model_name = self._resolve_model_name(frontend_model_name)
        logger.info(f"Resolved '{frontend_model_name}' to '{model_name}'")
        
        # Get model information
        model_info = self._get_model_info(model_name)
        if not model_info:
            # Try some common fallbacks
            fallback_models = [
                'Gemini 2.0 Flash',
                'gpt-4o-mini', 
                'Claude Sonnet 3.5',
                'DeepSeek-R1'
            ]
            
            for fallback in fallback_models:
                model_info = self._get_model_info(fallback)
                if model_info:
                    model_name = fallback
                    logger.info(f"Using fallback model: {model_name}")
                    break
            
            if not model_info:
                raise ValueError(f"Model '{frontend_model_name}' not found and no fallbacks available")
        
        provider_name = model_info['provider_name']
        provider_key = self._get_provider_key(provider_name)
        
        # Check if we have a client for this provider
        if provider_key not in self.clients:
            raise ValueError(f"No API client configured for provider '{provider_name}'. Please check your environment variables.")
        
        try:
            # Route to appropriate API based on provider
            if provider_key == 'openai':
                return self._call_openai_api(self.clients['openai'], model_name, message, max_tokens)
            
            elif provider_key == 'anthropic':
                return self._call_anthropic_api(self.clients['anthropic'], model_name, message, max_tokens)
            
            elif provider_key == 'google':
                return self._call_google_api(self.clients['google'], model_name, message)
            
            elif provider_key == 'deepseek':
                return self._call_openai_api(self.clients['deepseek'], model_name, message, max_tokens)
            
            elif provider_key == 'together':
                return self._call_openai_api(self.clients['together'], model_name, message, max_tokens)
            
            else:
                raise ValueError(f"No handler implemented for provider '{provider_name}'")
                
        except Exception as e:
            logger.error(f"Error generating response with {provider_name}: {e}")
            # Return a helpful error message instead of crashing
            error_msg = str(e)
            if "401" in error_msg or "authentication" in error_msg.lower():
                return f"⚠️ Authentication error with {provider_name}. Please check your API key configuration."
            elif "403" in error_msg or "forbidden" in error_msg.lower():
                return f"⚠️ Access denied to {provider_name}. You may need to upgrade your API plan."
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                return f"⚠️ Rate limit exceeded for {provider_name}. Please try again in a moment."
            elif "model" in error_msg.lower() and "not found" in error_msg.lower():
                return f"⚠️ Model '{model_name}' not available with {provider_name}. Please try a different model."
            else:
                return f"⚠️ Error with {provider_name}: {error_msg}. Please try a different model or check your configuration."
    
    def get_available_models(self):
        """Get list of available models that have configured API clients"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            available = []
            
            # Check all model tables (focusing on LLM models for chat)
            tables = ['llm_models', 'image_models', 'audio_models', 'video_models']
            
            for table in tables:
                try:
                    models = conn.execute(
                        f'SELECT model_name, provider_name FROM {table} WHERE is_active = 1'
                    ).fetchall()
                    
                    for model in models:
                        provider_key = self._get_provider_key(model['provider_name'])
                        if provider_key in self.clients:
                            available.append({
                                'model_name': model['model_name'],
                                'provider_name': model['provider_name'],
                                'table': table
                            })
                            
                except sqlite3.OperationalError:
                    # Table doesn't exist, continue to next
                    continue
            
            conn.close()
            return available
            
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return []