# api_tester.py (Version 4 - Final with Vertex AI)

import sqlite3
import os
import argparse
import time
from dotenv import load_dotenv
import requests

# Import provider-specific libraries
import openai
import anthropic

# --- Import BOTH Google Libraries ---
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
try:
    import vertexai
    from vertexai.preview.vision_models import ImageGenerationModel
    IS_VERTEX_AVAILABLE = True
except ImportError:
    IS_VERTEX_AVAILABLE = False


# --- Configuration ---
DATABASE_FILE_PATH = r"C:\Users\green\t3_clone\db\models.db"
OUTPUT_DIR = "output"
load_dotenv()

PROMPTS = {
    "llm": "Hello! In one sentence, tell me what you are.",
    "image": "A vibrant, photorealistic painting of a robot artist painting a sunset.",
    "audio": "Hello, this is a test of a text-to-speech synthesis model. I hope it sounds natural.",
    "video": "A 5-second, high-definition video of a futuristic city with flying cars."
}

# --- (Utility functions are unchanged) ---
def should_skip_model(api_name: str, notes: str) -> bool:
    api_name_lower = api_name.lower()
    notes_lower = notes.lower() if notes else ""
    skip_keywords = [
        "embedding", "rerank", "guard", "moderation", "retrieval",
        "computer-use", "search-preview", "realtime", "live", "dialog",
        "canny", "depth", "redux", "lora"
    ]
    for keyword in skip_keywords:
        if keyword in api_name_lower or keyword in notes_lower:
            print(f"🟡 SKIPPED: Model identified as '{keyword}' type, not suitable for this simple test.")
            return True
    return False

def save_output_file(content: bytes, model_type: str, api_name: str) -> str:
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    file_ext = {"image": "png", "audio": "mp3"}.get(model_type, "dat")
    safe_api_name = api_name.replace("/", "_").replace(":", "_")
    file_path = os.path.join(OUTPUT_DIR, f"{model_type}_{safe_api_name}.{file_ext}")
    with open(file_path, "wb") as f: f.write(content)
    return file_path

# --- Provider-Specific Handlers ---

def _handle_google_gemini_image(api_name, prompt):
    """Internal handler for Gemini API image models."""
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel(api_name)
    # This config is needed to tell Gemini you want an image back
    image_generation_config = GenerationConfig(response_mime_type="image/png")
    response = model.generate_content(prompt, generation_config=image_generation_config)
    if response.parts and hasattr(response.parts[0], 'inline_data'):
        image_bytes = response.parts[0].inline_data.data
        saved_path = save_output_file(image_bytes, "image", api_name)
        print(f"✅ Image Test Successful! Saved to: {saved_path}")
        return True
    else:
        print(f"🔴 ERROR: API call succeeded but no image data was found in the response.")
        return False

def _handle_google_vertex_image(api_name, prompt):
    """Internal handler for Vertex AI image models like Imagen."""
    if not IS_VERTEX_AVAILABLE:
        print("🔴 ERROR: 'google-cloud-aiplatform' library not installed. Cannot test Vertex AI models.")
        return False
        
    project_id = os.getenv("GOOGLE_PROJECT_ID")
    location = os.getenv("GOOGLE_LOCATION")
    if not project_id or not location:
        print("🔴 ERROR: GOOGLE_PROJECT_ID and GOOGLE_LOCATION must be set in .env for Vertex AI models.")
        return False

    vertexai.init(project=project_id, location=location)
    model = ImageGenerationModel.from_pretrained(api_name)
    response = model.generate_images(prompt=prompt, number_of_images=1)
    
    # Vertex returns a list of images, we save the first one
    image_bytes = response.images[0]._image_bytes
    saved_path = save_output_file(image_bytes, "image", api_name)
    print(f"✅ Image Test Successful! Saved to: {saved_path}")
    return True

def handle_google_request(api_name: str, prompt: str, model_type: str, notes: str) -> bool | str:
    """Main Google handler that routes to the correct internal handler."""
    if should_skip_model(api_name, notes): return 'skipped'
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("🔴 ERROR: GOOGLE_API_KEY not found in .env file.")
        return False
    
    try:
        if model_type == 'image':
            # --- THIS IS THE KEY LOGIC ---
            # If model name contains 'imagen', use the Vertex AI handler.
            # Otherwise, use the standard Gemini AI handler.
            if 'imagen' in api_name:
                return _handle_google_vertex_image(api_name, prompt)
            else:
                return _handle_google_gemini_image(api_name, prompt)
        
        # Logic for LLM and other types remains the same (using Gemini)
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(api_name)
        if model_type == 'audio':
            response = model.generate_content(prompt)
            saved_path = save_output_file(response.audio_content, model_type, api_name)
            print(f"✅ Audio Test Successful! Saved to: {saved_path}")
        else: # llm
            response = model.generate_content(prompt)
            print(f"✅ Chat Test Successful! Response: {response.text.strip()}")
        return True
            
    except Exception as e:
        print(f"🔴 ERROR: API call failed. Details: {e}")
        return False

# ... (All other handlers and main functions are unchanged and correct) ...
def handle_openai_request(api_name: str, prompt: str, model_type: str, notes: str) -> bool | str:
    if should_skip_model(api_name, notes): return 'skipped'
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key: return False
    client = openai.OpenAI(api_key=api_key)
    try:
        if model_type == 'image':
            response = client.images.generate(model=api_name, prompt=prompt, n=1, size="1024x1024")
            image_url = response.data[0].url
            image_bytes = requests.get(image_url).content
            saved_path = save_output_file(image_bytes, model_type, api_name)
            print(f"✅ Image Test Successful! Saved to: {saved_path}")
        elif model_type == 'audio':
            response = client.audio.speech.create(model=api_name, voice="alloy", input=prompt)
            saved_path = save_output_file(response.content, model_type, api_name)
            print(f"✅ Audio Test Successful! Saved to: {saved_path}")
        else:
            response = client.chat.completions.create(model=api_name, messages=[{"role": "user", "content": prompt}], max_tokens=50)
            print(f"✅ Chat Test Successful! Response: {response.choices[0].message.content.strip()}")
        return True
    except Exception as e:
        print(f"🔴 ERROR: API call failed. Details: {e}")
        return False
def handle_anthropic_request(api_name: str, prompt: str, model_type: str, notes: str) -> bool | str:
    if should_skip_model(api_name, notes) or model_type != 'llm': return 'skipped'
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key: return False
    client = anthropic.Anthropic(api_key=api_key)
    try:
        response = client.messages.create(model=api_name, messages=[{"role": "user", "content": prompt}], max_tokens=50)
        print(f"✅ Chat Test Successful! Response: {response.content[0].text.strip()}")
        return True
    except Exception as e:
        print(f"🔴 ERROR: API call failed. Details: {e}")
        return False
def handle_deepseek_request(api_name: str, prompt: str, model_type: str, notes: str) -> bool | str:
    if should_skip_model(api_name, notes) or model_type != 'llm': return 'skipped'
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key: return False
    client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
    try:
        response = client.chat.completions.create(model=api_name, messages=[{"role": "user", "content": prompt}], max_tokens=50)
        print(f"✅ Chat Test Successful! Response: {response.choices[0].message.content.strip()}")
        return True
    except Exception as e:
        print(f"🔴 ERROR: API call failed. Details: {e}")
        return False
def handle_cartesia_request(api_name: str, prompt: str, model_type: str, notes: str) -> bool | str:
    if should_skip_model(api_name, notes) or model_type != 'audio': return 'skipped'
    api_key = os.getenv("CARTESIA_API_KEY")
    if not api_key: return False
    try:
        headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
        payload = {"model_id": api_name, "transcript": prompt, "output_format": "mp3"}
        response = requests.post("https://api.cartesia.ai/v1/text-to-speech", headers=headers, json=payload)
        response.raise_for_status()
        saved_path = save_output_file(response.content, model_type, api_name)
        print(f"✅ Audio Test Successful! Saved to: {saved_path}")
        return True
    except Exception as e:
        print(f"🔴 ERROR: API call failed. Details: {e}")
        return False
def handle_togetherai_request(api_name: str, prompt: str, model_type: str, notes: str) -> bool | str:
    if should_skip_model(api_name, notes): return 'skipped'
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key: return False
    client = openai.OpenAI(api_key=api_key, base_url="https://api.together.xyz/v1")
    try:
        if model_type == 'image':
            response = client.images.generate(model=api_name, prompt=prompt, n=1, size="1024x1024")
            image_url = response.data[0].url
            image_bytes = requests.get(image_url).content
            saved_path = save_output_file(image_bytes, model_type, api_name)
            print(f"✅ Image Test Successful! Saved to: {saved_path}")
        elif model_type == 'llm':
            response = client.chat.completions.create(model=api_name, messages=[{"role": "user", "content": prompt}], max_tokens=50)
            print(f"✅ Chat Test Successful! Response: {response.choices[0].message.content.strip()}")
        else: return 'skipped'
        return True
    except Exception as e:
        print(f"🔴 ERROR: API call failed. Details: {e}")
        return False
def get_model_info(table: str, api_name: str):
    try:
        with sqlite3.connect(DATABASE_FILE_PATH) as conn:
            cursor = conn.cursor()
            query = f"SELECT provider_name, model_name, notes FROM {table} WHERE api_name = ?"
            return cursor.execute(query, (api_name,)).fetchone() or (None, None, None)
    except sqlite3.OperationalError: return None, None, None
def list_models(table: str):
    print(f"\n--- Active Models in table: {table} ---")
    try:
        with sqlite3.connect(DATABASE_FILE_PATH) as conn:
            cursor = conn.cursor()
            query = f"SELECT provider_name, model_name, api_name FROM {table} WHERE is_active = 1 ORDER BY provider_name, model_name"
            results = cursor.execute(query).fetchall()
            if not results: return
            print(f"{'Provider':<20} | {'Model Name':<45} | {'API Name'}")
            print("-" * 100)
            for row in results: print(f"{row[0]:<20} | {row[1]:<45} | {row[2]}")
    except sqlite3.OperationalError as e:
        print(f"🔴 Database Error: {e}.")
    print("-" * 100)
def test_all_models_in_table(table: str, model_type: str, prompt: str, handlers: dict):
    try:
        with sqlite3.connect(DATABASE_FILE_PATH) as conn:
            query = f"SELECT api_name, provider_name, model_name, notes FROM {table} WHERE is_active = 1 ORDER BY provider_name, model_name"
            all_models = conn.execute(query).fetchall()
    except sqlite3.OperationalError as e: return
    total_models = len(all_models)
    if not total_models: return
    success_count, failure_count, skipped_count = 0, 0, 0
    print(f"\n--- Starting bulk test for {total_models} active models in table: {table} ---")
    for i, (api_name, provider, model_name, notes) in enumerate(all_models):
        print("\n" + "="*80 + f"\n[{i+1}/{total_models}] Testing: {model_name} (Provider: {provider})\nAPI Name: {api_name}\n" + "="*80)
        handler = handlers.get(provider)
        if handler:
            result = handler(api_name, prompt, model_type, notes)
            if result is True: success_count += 1
            elif result is False: failure_count += 1
            elif result == 'skipped': skipped_count += 1
        else: skipped_count += 1
        time.sleep(1)
    print("\n" + "#"*50 + "\n" + " " * 18 + "BULK TEST SUMMARY" + "\n" + "#"*50)
    print(f"Table Tested:      {table}\nTotal Active:      {total_models}\n" + "-" * 25)
    print(f"✅ Successes:       {success_count}\n🔴 Failures:        {failure_count}\n🟡 Skipped:         {skipped_count}")
    print("#"*50)
def main():
    if not os.path.exists(DATABASE_FILE_PATH): return
    PROVIDER_HANDLERS = {
        "OpenAI": handle_openai_request, "Anthropic": handle_anthropic_request,
        "Google": handle_google_request, "DeepSeek": handle_deepseek_request,
        "Cartesia": handle_cartesia_request, "Together": handle_togetherai_request,
        "mistralai": handle_togetherai_request, "Nousresearch": handle_togetherai_request,
        "Qwen": handle_togetherai_request, "Meta": handle_togetherai_request,
        "Gryphe": handle_togetherai_request, "Arcee AI": handle_togetherai_request,
        "Alibaba Nlp": handle_togetherai_request, "BAAI": handle_togetherai_request,
        "Intfloat": handle_togetherai_request, "LG AI": handle_togetherai_request,
        "Mixedbread AI": handle_togetherai_request, "Refuel AI": handle_togetherai_request,
        "WhereIsAI": handle_togetherai_request, "nvidia": handle_togetherai_request,
        "salesforce": handle_togetherai_request, "google": handle_togetherai_request,
        "Black Forest Labs": handle_togetherai_request,
    }
    parser = argparse.ArgumentParser(description="Test AI Model APIs from a SQLite database.")
    subparsers = parser.add_subparsers(dest="model_type", required=True, help="The type of model to test.")
    for m_type in ["llm", "image", "audio", "video"]:
        p = subparsers.add_parser(m_type, help=f"Actions for {m_type.upper()} models.")
        p.add_argument("--prompt", default=PROMPTS[m_type], help="Custom prompt for the test.")
        action_group = p.add_mutually_exclusive_group(required=True)
        action_group.add_argument("--list", action="store_true")
        action_group.add_argument("--test", metavar="API_NAME")
        action_group.add_argument("--test-all", action="store_true")
    args = parser.parse_args()
    table_name = f"{args.model_type}_models"
    if args.list: list_models(table_name)
    elif args.test_all: test_all_models_in_table(table_name, args.model_type, args.prompt, PROVIDER_HANDLERS)
    elif args.test:
        provider, model_name, notes = get_model_info(table_name, args.test)
        if not provider: return
        print(f"\nTesting: '{model_name}' from '{provider}'")
        handler = PROVIDER_HANDLERS.get(provider)
        if handler: handler(args.test, args.prompt, args.model_type, notes)
if __name__ == "__main__": main()