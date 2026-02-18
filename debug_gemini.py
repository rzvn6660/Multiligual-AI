
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key found: {bool(api_key)}")

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')  # Try the one in brain.py
        print("Model initialized. Generating content...")
        response = model.generate_content("Hello, this is a test.")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

        # Try fallback model
        print("\nTrying gemini-1.5-flash...")
        try:
             model = genai.GenerativeModel('gemini-1.5-flash')
             response = model.generate_content("Hello")
             print(f"Response (Flash): {response.text}")
        except Exception as e2:
             print(f"Flash Error: {e2}")
