
from src.tts_provider import SantaliTTS
import os

tts = SantaliTTS()
tts.load_model()

# Text in Ol Chiki (Santali)
# "Johar" in Ol Chiki is roughly "ᱡᱚᱦᱟᱨ"
text_ol_chiki = "ᱡᱚᱦᱟᱨ" 

# Avoid printing unicode to windows console
# print(f"Testing TTS with Ol Chiki input: {text_ol_chiki}")
print("Testing TTS with Ol Chiki input...")
out_file = "test_olchiki.wav"

res = tts.speak_to_file(text_ol_chiki, out_file)

if res and os.path.exists(res):
    print("SUCCESS: TTS generated audio from Ol Chiki.")
    print(f"Size: {os.path.getsize(res)} bytes")
else:
    print("FAILURE: TTS failed for Ol Chiki.")
