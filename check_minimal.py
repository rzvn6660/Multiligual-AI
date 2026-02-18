import sys
print("Interpreter:", sys.executable)
try:
    print("Importing transformers...")
    import transformers
    print(f"Transformers: {transformers.__version__}")
except Exception as e:
    print(f"Transformers Error: {e}")

try:
    print("Importing onnxruntime...")
    import onnxruntime
    print(f"ONNX Runtime: {onnxruntime.__version__}")
except Exception as e:
    print(f"ONNX Runtime Error: {e}")

try:
    print("Importing torchaudio...")
    import torchaudio
    print(f"Torchaudio: {torchaudio.__version__}")
    backend = torchaudio.get_audio_backend()
    print(f"Audio Backend: {backend}")
except Exception as e:
    print(f"Torchaudio Error: {e}")
