import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
try:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    models = client.models.list()
    for m in models:
        print(f"Model: {m.name}")
except Exception as e:
    print(f"Error: {e}")
