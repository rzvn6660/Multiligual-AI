
from src.brain import get_gemini_response
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

print("Testing brain.get_gemini_response...")
try:
    response = get_gemini_response("What is the capital of India?")
    print(f"FINAL RESULT: {response}")
except Exception as e:
    print(f"CRITICAL FAIL: {e}")
