# media_client.py - Image and Video API Integration

import os
import sqlite3
from dotenv import load_dotenv
import logging
import requests
import base64
from io import BytesIO
from PIL import Image
import json

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

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MediaClient:
    def __init__(self, db_path):
        self.db_path = db_path
        self._setup_clients()
    
    def _setup_clients(self):
        """Initialize API clients for different providers"""
        self.clients = {}
        
        # OpenAI
        if openai and os.getenv("OPENAI_API_KEY"):
            self.clients['openai'] = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            logger.info("OpenAI client initialized for media")
        
        # Google
        if genai and os.getenv("GOOGLE_API_KEY"):
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.clients['google'] = genai
            logger.info("Google AI client initialized for media")
        
        # Together.ai (for Black Forest Labs models)
        if openai and os.getenv("TOGETHER_API_KEY"):
            self.clients['together'] = openai.OpenAI(
                api_key=os.getenv("TOGETHER_API_KEY"),
                base_url="https://api.together.xyz/v1"
            )
            logger.info("Together.ai client initialized for media")
    
    def _get_model_info(self, model_name, model_type):
        """Get model information from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            table_map = {
                'image': 'image_models',
                'video': 'video_models',
                'audio': 'audio_models'
            }
            
            table = table_map.get(model_type)
            if not table:
                return None
            
            model_info = conn.execute(
                f'SELECT * FROM {table} WHERE model_name = ? AND is_active = 1', 
                (model_name,)
            ).fetchone()
            
            conn.close()
            return dict(model_info) if model_info else None
            
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return None
    
    def _get_provider_key(self, provider_name):
        """Map provider names to client keys"""
        provider_map = {
            'OpenAI': 'openai',
            'Google': 'google',
            'Black Forest Labs': 'together',
            'Cartesia': 'together',  # Using Together.ai for now
        }
        return provider_map.get(provider_name, provider_name.lower())
    
    def _call_openai_image_api(self, client, model_name, prompt, **kwargs):
        """Call OpenAI image generation API"""
        try:
            model_info = self._get_model_info(model_name, 'image')
            api_name = model_info.get('api_name') if model_info else model_name
            
            response = client.images.generate(
                model=api_name,
                prompt=prompt,
                size=kwargs.get('size', '1024x1024'),
                quality=kwargs.get('quality', 'standard'),
                n=kwargs.get('n', 1)
            )
            
            return {
                'type': 'image',
                'images': [img.url for img in response.data],
                'model': model_name
            }
        except Exception as e:
            logger.error(f"OpenAI Image API error: {e}")
            raise
    
    def _call_google_image_api(self, genai_module, model_name, prompt, **kwargs):
        """Call Google image generation API"""
        try:
            model_info = self._get_model_info(model_name, 'image')
            api_name = model_info.get('api_name') if model_info else model_name
            
            model = genai_module.GenerativeModel(api_name)
            response = model.generate_content(prompt)
            
            # For Gemini image generation, the response format may vary
            # This is a placeholder implementation
            return {
                'type': 'image',
                'images': [response.text if hasattr(response, 'text') else str(response)],
                'model': model_name
            }
        except Exception as e:
            logger.error(f"Google Image API error: {e}")
            raise
    
    def _call_together_image_api(self, client, model_name, prompt, **kwargs):
        """Call Together.ai image generation API (for Black Forest Labs models)"""
        try:
            model_info = self._get_model_info(model_name, 'image')
            api_name = model_info.get('api_name') if model_info else model_name
            
            # Together.ai uses a different endpoint for image generation
            response = requests.post(
                "https://api.together.xyz/v1/images/generations",
                headers={
                    "Authorization": f"Bearer {os.getenv('TOGETHER_API_KEY')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": api_name,
                    "prompt": prompt,
                    "width": kwargs.get('width', 1024),
                    "height": kwargs.get('height', 1024),
                    "steps": kwargs.get('steps', 20),
                    "n": kwargs.get('n', 1)
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'type': 'image',
                    'images': [img['url'] for img in data['data']],
                    'model': model_name
                }
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.error(f"Together Image API error: {e}")
            raise
    
    def _call_google_video_api(self, genai_module, model_name, prompt, **kwargs):
        """Call Google video generation API"""
        try:
            model_info = self._get_model_info(model_name, 'video')
            api_name = model_info.get('api_name') if model_info else model_name
            
            model = genai_module.GenerativeModel(api_name)
            
            # For video generation, we might need different parameters
            generation_config = {
                "temperature": kwargs.get('temperature', 0.7),
                "max_output_tokens": kwargs.get('max_tokens', 1000),
            }
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return {
                'type': 'video',
                'videos': [response.text if hasattr(response, 'text') else str(response)],
                'model': model_name
            }
        except Exception as e:
            logger.error(f"Google Video API error: {e}")
            raise
    
    def generate_image(self, model_name, prompt, **kwargs):
        """
        Generate an image using the specified model
        
        Args:
            model_name: The display name of the image model
            prompt: The text prompt for image generation
            **kwargs: Additional parameters like size, quality, etc.
            
        Returns:
            dict: Response containing generated image URLs
        """
        model_info = self._get_model_info(model_name, 'image')
        if not model_info:
            raise ValueError(f"Image model '{model_name}' not found")
        
        provider_name = model_info['provider_name']
        provider_key = self._get_provider_key(provider_name)
        
        if provider_key not in self.clients:
            raise ValueError(f"No API client configured for provider '{provider_name}'")
        
        try:
            if provider_key == 'openai':
                return self._call_openai_image_api(self.clients['openai'], model_name, prompt, **kwargs)
            elif provider_key == 'google':
                return self._call_google_image_api(self.clients['google'], model_name, prompt, **kwargs)
            elif provider_key == 'together':
                return self._call_together_image_api(self.clients['together'], model_name, prompt, **kwargs)
            else:
                raise ValueError(f"No image handler implemented for provider '{provider_name}'")
                
        except Exception as e:
            logger.error(f"Error generating image with {provider_name}: {e}")
            error_msg = str(e)
            if "401" in error_msg or "authentication" in error_msg.lower():
                return f"⚠️ Authentication error with {provider_name}. Please check your API key configuration."
            elif "403" in error_msg or "forbidden" in error_msg.lower():
                return f"⚠️ Access denied to {provider_name}. You may need to upgrade your API plan."
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                return f"⚠️ Rate limit exceeded for {provider_name}. Please try again in a moment."
            else:
                return f"⚠️ Error with {provider_name}: {error_msg}. Please try a different model or check your configuration."
    
    def generate_video(self, model_name, prompt, **kwargs):
        """
        Generate a video using the specified model
        
        Args:
            model_name: The display name of the video model
            prompt: The text prompt for video generation
            **kwargs: Additional parameters
            
        Returns:
            dict: Response containing generated video URLs
        """
        model_info = self._get_model_info(model_name, 'video')
        if not model_info:
            raise ValueError(f"Video model '{model_name}' not found")
        
        provider_name = model_info['provider_name']
        provider_key = self._get_provider_key(provider_name)
        
        if provider_key not in self.clients:
            raise ValueError(f"No API client configured for provider '{provider_name}'")
        
        try:
            if provider_key == 'google':
                return self._call_google_video_api(self.clients['google'], model_name, prompt, **kwargs)
            else:
                raise ValueError(f"No video handler implemented for provider '{provider_name}'")
                
        except Exception as e:
            logger.error(f"Error generating video with {provider_name}: {e}")
            error_msg = str(e)
            if "401" in error_msg or "authentication" in error_msg.lower():
                return f"⚠️ Authentication error with {provider_name}. Please check your API key configuration."
            elif "403" in error_msg or "forbidden" in error_msg.lower():
                return f"⚠️ Access denied to {provider_name}. You may need to upgrade your API plan."
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                return f"⚠️ Rate limit exceeded for {provider_name}. Please try again in a moment."
            else:
                return f"⚠️ Error with {provider_name}: {error_msg}. Please try a different model or check your configuration."
    
    def get_available_models(self, model_type):
        """Get list of available models by type"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            table_map = {
                'image': 'image_models',
                'video': 'video_models',
                'audio': 'audio_models'
            }
            
            table = table_map.get(model_type)
            if not table:
                return []
            
            models = conn.execute(
                f'SELECT model_name, provider_name FROM {table} WHERE is_active = 1'
            ).fetchall()
            
            available = []
            for model in models:
                provider_key = self._get_provider_key(model['provider_name'])
                if provider_key in self.clients:
                    available.append({
                        'model_name': model['model_name'],
                        'provider_name': model['provider_name'],
                        'type': model_type
                    })
            
            conn.close()
            return available
            
        except Exception as e:
            logger.error(f"Error getting available {model_type} models: {e}")
            return []