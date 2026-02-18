
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

try:
    print("Listing models...")
    # New SDK list_models returns an iterator of Model objects
    # We need to see how to access them, usually model.name
    # Note: client.models.list() might differ in arguments
    
    # Try the correct v2 SDK list method
    pager = client.models.list() 
    
    found_any = False
    for model in pager:
        print(f" - {model.name} (methods: {model.supported_generation_methods})")
        found_any = True
        
    if not found_any:
        print("No models found.")
        
except Exception as e:
    print(f"Error listing: {e}")
