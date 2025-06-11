#!/usr/bin/env python3
"""
Test script to verify AI API integration is working correctly.
Run this script to test your API keys and AI client setup.
"""

import os
import sys
from dotenv import load_dotenv
from ai_client import AIClient

# Load environment variables
load_dotenv()

def test_ai_integration():
    """Test the AI client with available providers"""
    
    print("🧪 Testing T3 Chat AI Integration")
    print("=" * 50)
    
    # Check if database exists
    db_path = "db/models.db"
    if not os.path.exists(db_path):
        print("❌ Database not found!")
        print(f"   Expected location: {db_path}")
        print("   Please run: sqlite3 db/models.db < create_db.sql")
        return False
    
    print("✅ Database found")
    
    # Initialize AI client
    try:
        ai_client = AIClient(db_path)
        print("✅ AI Client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize AI Client: {e}")
        return False
    
    # Check available models
    available_models = ai_client.get_available_models()
    
    if not available_models:
        print("\n❌ No models available!")
        print("   This usually means no API keys are configured.")
        print("   Please check your .env file and add at least one API key:")
        print("   - OPENAI_API_KEY")
        print("   - ANTHROPIC_API_KEY") 
        print("   - GOOGLE_API_KEY")
        print("   - DEEPSEEK_API_KEY")
        print("   - TOGETHER_API_KEY")
        return False
    
    print(f"\n✅ Found {len(available_models)} available models:")
    
    # Group by provider
    providers = {}
    for model in available_models:
        provider = model['provider_name']
        if provider not in providers:
            providers[provider] = []
        providers[provider].append(model['model_name'])
    
    for provider, models in providers.items():
        print(f"   📦 {provider}: {len(models)} models")
        for model in models[:3]:  # Show first 3 models
            print(f"      - {model}")
        if len(models) > 3:
            print(f"      ... and {len(models) - 3} more")
    
    # Test with the first available model
    test_model = available_models[0]
    model_name = test_model['model_name']
    provider_name = test_model['provider_name']
    
    print(f"\n🔬 Testing with {model_name} ({provider_name})...")
    
    test_message = "Hello! Please respond with 'AI test successful' if you can read this."
    
    try:
        response = ai_client.generate_response(model_name, test_message, max_tokens=50)
        print("✅ Test successful!")
        print(f"   Model: {model_name}")
        print(f"   Response: {response[:100]}{'...' if len(response) > 100 else ''}")
        
        # Test markdown formatting
        print("\n🎨 Testing markdown formatting...")
        markdown_test = """**Bold text**, *italic text*, and `code text`. 

Here's a list:
- Item 1
- Item 2

```python
print("Hello, World!")
```
"""
        formatted_response = ai_client.generate_response(model_name, 
            "Please format this text with markdown: " + markdown_test, max_tokens=100)
        print("✅ Markdown test successful!")
        print(f"   Response: {formatted_response[:150]}{'...' if len(formatted_response) > 150 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def check_api_keys():
    """Check which API keys are configured"""
    print("\n🔑 Checking API Key Configuration")
    print("-" * 40)
    
    api_keys = {
        'OpenAI': 'OPENAI_API_KEY',
        'Anthropic': 'ANTHROPIC_API_KEY', 
        'Google AI': 'GOOGLE_API_KEY',
        'DeepSeek': 'DEEPSEEK_API_KEY',
        'Together.ai': 'TOGETHER_API_KEY'
    }
    
    configured_count = 0
    
    for provider, env_var in api_keys.items():
        key = os.getenv(env_var)
        if key:
            # Mask the key for security
            masked_key = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
            print(f"✅ {provider}: {masked_key}")
            configured_count += 1
        else:
            print(f"❌ {provider}: Not configured")
    
    print(f"\nTotal configured: {configured_count}/{len(api_keys)}")
    
    if configured_count == 0:
        print("\n⚠️  No API keys found!")
        print("   Please add at least one API key to your .env file.")
        print("   Copy .env.example to .env and fill in your keys.")
        return False
    
    return True

def main():
    """Main test function"""
    print("T3 Chat AI Integration Test")
    print("This script tests your AI API setup\n")
    
    # Check API keys first
    if not check_api_keys():
        sys.exit(1)
    
    # Test AI integration
    if not test_ai_integration():
        print("\n❌ AI integration test failed!")
        print("   Check the error messages above and verify your API keys.")
        sys.exit(1)
    
    print("\n🎉 All tests passed!")
    print("   Your T3 Chat AI integration is working correctly.")
    print("   You can now run: python app.py")

if __name__ == "__main__":
    main()