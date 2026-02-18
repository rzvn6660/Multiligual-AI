
import os
import torch
import soundfile as sf
from src.tts_provider import SantaliTTS
from src.utils import setup_logger

logger = setup_logger("TTS_Test")

def test_tts():
    print("Initializing TTS...")
    try:
        tts = SantaliTTS()
        if not tts.load_model():
            print("Failed to load TTS model")
            return

        text = "Johar, cheleka menama?" # "Hello, how are you?" in Santali
        output_file = "test_tts_output.wav"
        
        print(f"Generating audio for: {text}")
        result_path = tts.speak_to_file(text, output_file)
        
        if result_path and os.path.exists(result_path):
            print(f"SUCCESS: Audio saved to {result_path}")
            print(f"File size: {os.path.getsize(result_path)} bytes")
        else:
            print("FAILURE: output file not generated or returned None")
            
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tts()
