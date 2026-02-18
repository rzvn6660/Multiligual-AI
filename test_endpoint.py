
import requests
import wave
import struct

# Create a dummy WAV file
def create_dummy_wav(filename):
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        # Write 1 second of silence/dummy data
        data = struct.pack('<h', 0) * 16000
        f.writeframes(data)
    print(f"Created {filename}")

create_dummy_wav("test_audio_endpoint.wav")

# Try to fetch it via local server
try:
    url = "http://localhost:5000/api/audio/test_audio_endpoint.wav"
    print(f"Fetching {url}...")
    response = requests.get(url)
    
    if response.status_code == 200:
        print(f"SUCCESS: Fetched {len(response.content)} bytes")
        # Save received to verify
        with open("received_test.wav", "wb") as f:
            f.write(response.content)
    else:
        print(f"FAILURE: Status Code {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"ERROR: {e}")
