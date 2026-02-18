
import os
from dotenv import load_dotenv
from google import genai
import time

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

models_to_try = [
    "gemini-flash-latest",
    "gemini-2.5-flash", 
    "gemini-2.0-flash-lite",
    "models/gemini-embedding-001" # Just to see if *anything* works, though it's embedding
]

for m in models_to_try:
    print(f"Trying {m}...")
    try:
        response = client.models.generate_content(
            model=m,
            contents="Hi"
        )
        print(f"SUCCESS with {m}: {response.text}")
        break
    except Exception as e:
        print(f"Failed {m}: {e}")
        time.sleep(1)
