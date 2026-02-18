
import requests

try:
    print("Pinging server...")
    # Send without file to trigger 400
    res = requests.post("http://localhost:5000/api/process")
    print(f"Status: {res.status_code}")
    print(f"Json: {res.json()}")
except Exception as e:
    print(f"Error: {e}")
