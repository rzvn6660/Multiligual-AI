
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

try:
    print("Testing gemini-1.5-flash with NEW SDK...")
    resp = client.models.generate_content(model="gemini-1.5-flash", contents="Hi")
    print(f"SUCCESS: {resp.text}")
except Exception as e:
    print(f"FAILED: {e}")
