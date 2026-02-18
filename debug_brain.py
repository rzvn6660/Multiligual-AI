
import os
import sys
from src.config_hf import Config
from src.utils import setup_logger
import google.generativeai as genai

# Setup basic logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DebugBrain")

def test_gemini():
    print("--- Testing Gemini Configuration ---")
    api_key = Config.GEMINI_API_KEY
    if not api_key:
        print("ERROR: GEMINI_API_KEY is missing or empty.")
        return

    print(f"API Key present: Yes (Length: {len(api_key)})")
    print(f"Model Name: {getattr(Config, 'GEMINI_MODEL', 'Not Set')}")
    
    try:
        genai.configure(api_key=api_key)
        model_name = getattr(Config, 'GEMINI_MODEL', 'gemini-1.5-flash')
        print(f"Initializing model: {model_name}")
        
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello, reply with 'Working'.")
        
        print(f"Response: {response.text}")
        print("--- SUCCESS ---")
        
    except Exception as e:
        print(f"--- FAILURE ---")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gemini()
