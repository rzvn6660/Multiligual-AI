
import os
import sys
from unittest.mock import MagicMock, patch

# Mock imports so we don't need actual keys/dependencies
sys.modules['groq'] = MagicMock()
sys.modules['google'] = MagicMock()
sys.modules['google.genai'] = MagicMock()
msg_mock = MagicMock()
msg_mock.choices = [MagicMock()]
msg_mock.choices[0].message.content = "Groq Response"

# Setup environment
os.environ['GROQ_API_KEY'] = 'gsk_mock_key'
os.environ['GEMINI_API_KEY'] = 'mock_gemini_key'

# Mock Groq Client
mock_groq_client = MagicMock()
mock_groq_client.chat.completions.create.return_value = msg_mock
sys.modules['groq'].Groq.return_value = mock_groq_client

# Import brain
from src import brain

print("--- Test 1: Groq Priority ---")
# Call
response = brain.get_ai_response("Test")
print(f"Response: {response}")

# Verify Order
print("\n--- Verifying Calls ---")
if mock_groq_client.chat.completions.create.called:
    print("SUCCESS: Groq was called first.")
else:
    print("FAILURE: Groq was NOT called.")

# Reset and fail Groq to test fallback
print("\n--- Test 2: Gemini Fallback ---")
mock_groq_client.chat.completions.create.side_effect = Exception("Groq Dead")
mock_gemini_client = MagicMock()
mock_gemini_client.models.generate_content.return_value.text = "Gemini Response"
sys.modules['google'].genai.Client.return_value = mock_gemini_client

response = brain.get_ai_response("Test 2")
print(f"Response: {response}")

if mock_gemini_client.models.generate_content.called:
    print("SUCCESS: Gemini was called after Groq failure.")
else:
    print("FAILURE: Gemini was NOT called.")
