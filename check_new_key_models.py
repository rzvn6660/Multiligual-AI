
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print(f"Checking models for key ending in ...{api_key[-4:]}")

try:
    # List models to see what's available
    print("Available 'generateContent' models:")
    # Note: list method might vary by SDK version, sticking to client.models.list()
    for m in client.models.list():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"List failed: {e}")

# Test the most likely free tier candidates
candidates = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash-001",
    "gemini-flash-latest", # worked before
    "gemini-2.0-flash" 
]

print("\nTesting Candidates:")
for model in candidates:
    print(f"Testing {model}...")
    try:
        resp = client.models.generate_content(
            model=model, 
            contents="Test"
        )
        print(f"SUCCESS: {model}")
    except Exception as e:
        print(f"FAILED {model}: {e}")
