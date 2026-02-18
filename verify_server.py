
import requests
import time
import sys

print("Attempting to connect to server...")
for i in range(10):
    try:
        response = requests.get("http://localhost:5000/api/status")
        if response.status_code == 200:
            print("SUCCESS: Server is Online")
            print(f"Status: {response.json()}")
            sys.exit(0)
    except requests.exceptions.ConnectionError:
        print(f"Attempt {i+1}: Server not ready yet...")
        time.sleep(2)
        
print("FAILURE: Could not connect after 10 attempts")
sys.exit(1)
