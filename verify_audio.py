
from src.tts_provider import SantaliTTS
import os

print("Testing TTS Audio Generation...")
tts = SantaliTTS()
loaded = tts.load_model()
if not loaded:
    print("Failed to load model.")
    exit(1)

text = "Johar ge, cheleka menama?"
output = "audio_test.wav"
f = tts.speak_to_file(text, output)

if f and os.path.exists(output):
    size = os.path.getsize(output)
    print(f"SUCCESS: Generated {output} ({size} bytes)")
else:
    print("FAILURE: No audio file generated.")
