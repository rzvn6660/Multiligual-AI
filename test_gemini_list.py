
import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

def test_gemini_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY Missing")
        return

    genai.configure(api_key=api_key)
    
    # Models to test
    models = [
        'models/gemini-1.5-flash',
        'gemini-1.5-flash', 
        'models/gemini-1.5-pro',
        'gemini-1.5-pro',
        'models/gemini-pro',
        'gemini-pro'
    ]
    
    print(f"Testing {len(models)} models with Key ending in ...{api_key[-4:]}")
    
    for m in models:
        print(f"\n--- Testing: {m} ---")
        try:
            model = genai.GenerativeModel(m)
            response = model.generate_content("Say 'OK'")
            print(f"SUCCESS: {response.text.strip()}")
            return # Stop after first success if that's what we want to validate
        except Exception as e:
            print(f"FAILED: {e}")

if __name__ == "__main__":
    test_gemini_models()
