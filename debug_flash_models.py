
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

print("Listing FLASH models...")
for model in client.models.list():
    if 'flash' in model.name:
        print(f" - {model.name}")
