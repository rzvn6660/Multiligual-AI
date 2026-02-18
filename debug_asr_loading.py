
print("Starting check...")
try:
    import torch
    print(f"Torch: {torch.__version__}")
    import nemo
    print(f"NeMo: {nemo.__version__}")
    from src.asr_provider import SantaliASR
    print("Provider imported.")
    asr = SantaliASR()
    print("Loading model...")
    success = asr.load_model()
    print(f"Load Result: {success}")
except Exception as e:
    print(f"CRASH: {e}")
    import traceback
    traceback.print_exc()
