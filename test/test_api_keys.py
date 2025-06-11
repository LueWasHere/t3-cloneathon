#!/usr/bin/env python3
"""
Test individual API keys to see which ones work
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_openai():
    """Test OpenAI API"""
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'OpenAI test successful'"}],
            max_tokens=20
        )
        print("✅ OpenAI: " + response.choices[0].message.content.strip())
        return True
    except Exception as e:
        print(f"❌ OpenAI: {e}")
        return False

def test_anthropic():
    """Test Anthropic API"""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            messages=[{"role": "user", "content": "Say 'Anthropic test successful'"}],
            max_tokens=20
        )
        print("✅ Anthropic: " + response.content[0].text.strip())
        return True
    except Exception as e:
        print(f"❌ Anthropic: {e}")
        return False

def test_google():
    """Test Google API"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Say 'Google test successful'")
        print("✅ Google: " + response.text.strip())
        return True
    except Exception as e:
        print(f"❌ Google: {e}")
        return False

def test_deepseek():
    """Test DeepSeek API"""
    try:
        import openai
        client = openai.OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1"
        )
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "Say 'DeepSeek test successful'"}],
            max_tokens=20
        )
        print("✅ DeepSeek: " + response.choices[0].message.content.strip())
        return True
    except Exception as e:
        print(f"❌ DeepSeek: {e}")
        return False

def test_together():
    """Test Together.ai API"""
    try:
        import openai
        client = openai.OpenAI(
            api_key=os.getenv("TOGETHER_API_KEY"),
            base_url="https://api.together.xyz/v1"
        )
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            messages=[{"role": "user", "content": "Say 'Together test successful'"}],
            max_tokens=20
        )
        print("✅ Together.ai: " + response.choices[0].message.content.strip())
        return True
    except Exception as e:
        print(f"❌ Together.ai: {e}")
        return False

def main():
    print("🔧 Testing Individual API Keys")
    print("=" * 40)
    
    working_apis = 0
    
    tests = [
        ("OpenAI", test_openai, "OPENAI_API_KEY"),
        ("Anthropic", test_anthropic, "ANTHROPIC_API_KEY"), 
        ("Google", test_google, "GOOGLE_API_KEY"),
        ("DeepSeek", test_deepseek, "DEEPSEEK_API_KEY"),
        ("Together.ai", test_together, "TOGETHER_API_KEY")
    ]
    
    available_tests = 0
    
    for name, test_func, env_var in tests:
        api_key = os.getenv(env_var)
        if api_key:
            available_tests += 1
            print(f"\n🔑 Testing {name}...")
            if test_func():
                working_apis += 1
        else:
            print(f"\n⏭️  Skipping {name} (no API key)")
    
    print(f"\n📊 Results: {working_apis}/{available_tests} APIs working")
    
    if working_apis > 0:
        print("🎉 You have working API keys! Try using a working provider in the chat.")
    else:
        print("❌ No working API keys found. Please check your .env file.")

if __name__ == "__main__":
    main()