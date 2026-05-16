import os
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env file
load_dotenv()

def test_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env")
        return

    print(f"Testing Gemini API with key: {api_key[:10]}...")

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say 'Hello, the Gemini API is working!'"
        )
        print("Success! Gemini response:")
        print(response.text)
    except Exception as e:
        print("Failed to connect to Gemini:")
        print(e)

if __name__ == "__main__":
    test_gemini()
