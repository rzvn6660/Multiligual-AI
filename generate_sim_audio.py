
from src.tts_provider import SantaliTTS
import os

tts = SantaliTTS()
tts.load_model()
tts.speak_to_file("Johar", "sim_input.wav")
print("Generated sim_input.wav")
