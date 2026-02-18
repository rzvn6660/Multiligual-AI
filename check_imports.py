
try:
    print("Importing torch...")
    import torch
    print(f"Torch: {torch.__version__}, CUDA: {torch.version.cuda}, Available: {torch.cuda.is_available()}")
except ImportError as e:
    print(f"Torch failed: {e}")

try:
    print("Importing transformers...")
    import transformers
    print(f"Transformers: {transformers.__version__}")
except ImportError as e:
    print(f"Transformers failed: {e}")

try:
    print("Importing parler_tts...")
    import parler_tts
    print("Parler TTS imported")
except ImportError as e:
    print(f"Parler TTS failed: {e}")

try:
    print("Importing onnxruntime...")
    import onnxruntime
    print(f"ONNX Runtime: {onnxruntime.__version__}")
except ImportError as e:
    print(f"ONNX Runtime failed: {e}")
