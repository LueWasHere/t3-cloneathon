#!/usr/bin/env python3
"""
Debug script to test the chat integration and identify issues
Run this to diagnose chat problems in your T3 Chat application
"""

import os
import sys
import sqlite3
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_database():
    """Check database structure and content"""
    print("🔍 Checking Database Structure...")
    db_path = "db/models.db"
    
    if not os.path.exists(db_path):
        print("❌ Database not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if llm_models table exists and has data
        cursor.execute("SELECT COUNT(*) FROM llm_models WHERE is_active = 1")
        active_models = cursor.fetchone()[0]
        print(f"✅ Found {active_models} active LLM models")
        
        # Get a sample of available models
        cursor.execute("""
            SELECT provider_name, model_name, api_name 
            FROM llm_models 
            WHERE is_active = 1 
            LIMIT 5
        """)
        sample_models = cursor.fetchall()
        
        print("📋 Sample models:")
        for provider, model, api_name in sample_models:
            print(f"   - {provider}: {model} (API: {api_name})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_api_keys():
    """Check which API keys are configured"""
    print("\n🔑 Checking API Keys...")
    
    api_keys = {
        'OpenAI': 'OPENAI_API_KEY',
        'Anthropic': 'ANTHROPIC_API_KEY',
        'Google': 'GOOGLE_API_KEY',
        'DeepSeek': 'DEEPSEEK_API_KEY',
        'Together.ai': 'TOGETHER_API_KEY'
    }
    
    configured_keys = []
    
    for provider, env_var in api_keys.items():
        key = os.getenv(env_var)
        if key:
            masked_key = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
            print(f"✅ {provider}: {masked_key}")
            configured_keys.append(provider)
        else:
            print(f"❌ {provider}: Not configured")
    
    return configured_keys

def test_ai_client():
    """Test AI client initialization"""
    print("\n🤖 Testing AI Client...")
    
    try:
        # Import and initialize AI client
        from ai_client import AIClient
        
        db_path = "db/models.db"
        ai_client = AIClient(db_path)
        
        # Get available models
        available_models = ai_client.get_available_models()
        
        if not available_models:
            print("❌ No models available!")
            print("   This usually means no API keys are configured.")
            return None
        
        print(f"✅ AI Client initialized with {len(available_models)} available models")
        
        # Group by provider
        providers = {}
        for model in available_models:
            provider = model['provider_name']
            if provider not in providers:
                providers[provider] = []
            providers[provider].append(model['model_name'])
        
        for provider, models in providers.items():
            print(f"   📦 {provider}: {len(models)} models")
        
        return ai_client
        
    except Exception as e:
        print(f"❌ AI Client error: {e}")
        return None

def test_model_selection():
    """Test model selection and mapping"""
    print("\n🎯 Testing Model Selection...")
    
    try:
        conn = sqlite3.connect("db/models.db")
        cursor = conn.cursor()
        
        # Test some common model name mappings
        test_models = [
            'Gemini 2.5 Flash',
            'Claude 4 Sonnet', 
            'GPT-4o',
            'DeepSeek R1',
            'Llama 4 Scout'
        ]
        
        for display_name in test_models:
            # Try to find model by display name or similar
            cursor.execute("""
                SELECT model_name, api_name, provider_name 
                FROM llm_models 
                WHERE model_name LIKE ? OR model_name = ?
                AND is_active = 1
                LIMIT 1
            """, (f"%{display_name}%", display_name))
            
            result = cursor.fetchone()
            if result:
                model_name, api_name, provider = result
                print(f"✅ {display_name} → {model_name} (API: {api_name})")
            else:
                print(f"❌ {display_name} → Not found in database")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Model selection test error: {e}")

def test_chat_endpoint():
    """Test a sample chat request"""
    print("\n💬 Testing Chat Functionality...")
    
    ai_client = test_ai_client()
    if not ai_client:
        return False
    
    # Get first available model
    available_models = ai_client.get_available_models()
    if not available_models:
        print("❌ No models available for testing")
        return False
    
    test_model = available_models[0]['model_name']
    print(f"🧪 Testing with model: {test_model}")
    
    try:
        response = ai_client.generate_response(
            test_model, 
            "Hello! Please respond with 'Test successful' if you can read this.",
            max_tokens=50
        )
        
        print(f"✅ Chat test successful!")
        print(f"   Response: {response[:100]}{'...' if len(response) > 100 else ''}")
        return True
        
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False

def check_flask_routes():
    """Check if Flask routes are properly configured"""
    print("\n🌐 Checking Flask Configuration...")
    
    try:
        # Try to import the main app
        from app import app
        
        # Get all routes
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append((rule.rule, list(rule.methods)))
        
        print("📍 Available routes:")
        for route, methods in routes:
            if route in ['/chat', '/models', '/models/available']:
                print(f"   ✅ {route} {methods}")
            else:
                print(f"   📄 {route} {methods}")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask import error: {e}")
        return False

def main():
    """Main diagnostic function"""
    print("🔧 T3 Chat Diagnostic Tool")
    print("=" * 50)
    
    all_checks = [
        check_database(),
        len(check_api_keys()) > 0,
        test_ai_client() is not None,
        check_flask_routes(),
        test_chat_endpoint()
    ]
    
    passed = sum(all_checks)
    total = len(all_checks)
    
    print(f"\n📊 Diagnostic Summary: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! Your chat should be working.")
    else:
        print("⚠️  Some issues found. Please address them:")
        if not all_checks[0]:
            print("   - Check database setup")
        if not all_checks[1]:
            print("   - Configure API keys in .env file")
        if not all_checks[2]:
            print("   - Fix AI client initialization")
        if not all_checks[3]:
            print("   - Check Flask app configuration")
        if not all_checks[4]:
            print("   - Test individual API providers")

if __name__ == "__main__":
    main()