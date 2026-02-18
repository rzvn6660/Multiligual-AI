
import os
import sys
from dotenv import load_dotenv

# Ensure we can import from src
sys.path.append(os.getcwd())
load_dotenv()

# Import the actual function getting used
from src.brain import get_gemini_response

print("Testing brain.get_gemini_response...")
try:
    response = get_gemini_response("Hello")
    print(f"Result: {response}")
except Exception as e:
    print(f"FAILED: {e}")
