
import sys
import os

print("Checking full setup...")

try:
    import pyaudio
    print("pyaudio: OK")
    p = pyaudio.PyAudio()
    count = p.get_device_count()
    print(f"Audio Devices found: {count}")
    p.terminate()
except ImportError:
    print("pyaudio: MISSING")
except Exception as e:
    print(f"pyaudio error: {e}")

try:
    import torch
    print(f"torch: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
except ImportError:
    print("torch: MISSING")

try:
    import nemo
    print("nemo: OK")
except ImportError:
    print("nemo: MISSING")

try:
    import parler_tts
    print("parler_tts: OK")
except ImportError:
    print("parler_tts: MISSING")

try:
    import transformers
    print("transformers: OK")
except ImportError:
    print("transformers: MISSING")

try:
    import dotenv
    print("python-dotenv: OK")
except ImportError:
    print("python-dotenv: MISSING")

if os.path.exists("ffmpeg.exe"):
    print("ffmpeg.exe: FOUND in current dir")
else:
    print("ffmpeg.exe: NOT FOUND in current dir (might be in PATH)")

print("Check complete.")
