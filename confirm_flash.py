
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

model = "gemini-flash-latest" 
print(f"Testing {model}...")
try:
    resp = client.models.generate_content(model=model, contents="Hi")
    print(f"SUCCESS: {resp.text}")
except Exception as e:
    print(f"FAILED: {e}")
