
import os
from dotenv import load_dotenv
from google import genai
import sys

# Load env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"API Key found: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"Key preview: {api_key[:5]}...")

try:
    print("Initializing Client...")
    client = genai.Client(api_key=api_key)
    
    print("Testing generate_content with 'gemini-1.5-flash'...")
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Hello, are you working?"
    )
    
    print("--- SUCCESS ---")
    print(f"Response: {response.text}")

except Exception as e:
    print("\n--- FAILURE ---")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {e}")
    import traceback
    traceback.print_exc()
