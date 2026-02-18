
import os
from huggingface_hub import login
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("HF_TOKEN")
if not token:
    print("HF_TOKEN not found in .env file.")
else:
    print(f"Found token: {token[:5]}...{token[-3:]}")
    try:
        login(token=token)
        print("Successfully logged in to Hugging Face!")
    except Exception as e:
        print(f"Login failed: {e}")
