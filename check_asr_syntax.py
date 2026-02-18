
try:
    from src.asr_provider import SantaliASR
    print("ASR Provider imported successfully.")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
