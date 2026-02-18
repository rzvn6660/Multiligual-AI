
import os
import sys
from dotenv import load_dotenv

# Explicitly load .env from the current directory
load_dotenv('.env')

# Add src to path
sys.path.append(os.getcwd())

from src.brain import get_gemini_response
from src.config_hf import Config

print("--- Debugging Brain Module ---")
print(f"Environment Key: {os.getenv('GEMINI_API_KEY')[:5]}...")
print(f"Config Key: {Config.GEMINI_API_KEY[:5]}...")

print("\nCalling get_gemini_response('Hello')...")
try:
    response = get_gemini_response("Hello")
    print(f"\nFinal Response: {response}")
except Exception as e:
    print(f"\nCRITICAL EXCEPTION: {e}")
