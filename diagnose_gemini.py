
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Force reload of .env
load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY")

print(f"Checking Gemini Configuration...")
print(f"API Key Environment Variable Found: {'Yes' if api_key else 'No'}")

if api_key:
    # Print first few chars to verify it's not a placeholder (don't print full key)
    print(f"API Key Start: {api_key[:4]}...")
    
    try:
        genai.configure(api_key=api_key)
        print("\nAttempting to list available models...")
        models = list(genai.list_models())
        print(f"Found {len(models)} models.")
        
        generate_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        print("\nModels supporting generateContent:")
        for m in generate_models:
            print(f" - {m}")
            
        # Try generation with the first valid model
        if generate_models:
            test_model = 'gemini-1.5-flash' if 'models/gemini-1.5-flash' in generate_models else generate_models[0]
            if 'models/' not in test_model: test_model = f"models/{test_model}" # specific handling
            
            # Correction: genai.GenerativeModel takes the name without 'models/' prefix sometimes, or with.
            # Best to use the name as returned by list_models, often 'models/gemini-pro'
            
            print(f"\nTesting generation with: {test_model}")
            model = genai.GenerativeModel(test_model)
            response = model.generate_content("Explain 'Hello' in one word.")
            print(f"Success! Response: {response.text}")
            
    except Exception as e:
        print(f"\nERROR: {e}")
else:
    print("ERROR: GEMINI_API_KEY is not set in .env file.")
