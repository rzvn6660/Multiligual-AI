import requests
import json

def test_models():
    models = ["phi3", "llama3"]
    question = "What is rain? Please explain simply."
    
    for model in models:
        print(f"=====================================")
        print(f"Asking {model.upper()}: '{question}'\n")
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": question}
            ],
            "stream": False
        }
        
        try:
            res = requests.post('http://127.0.0.1:11434/api/chat', json=payload, timeout=120)
            if res.status_code == 200:
                data = res.json()
                answer = data.get("message", {}).get("content", "No answer found")
                print(f"{model.upper()} Answer:\n")
                print(answer)
                print("\n")
            else:
                print(f"Error: Server returned status {res.status_code}")
        except Exception as e:
            print(f"Connection Failed: {e}")

if __name__ == "__main__":
    test_models()
