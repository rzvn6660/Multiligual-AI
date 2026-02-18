from transformers import AutoModel
import torch
import torchaudio
import os
import numpy as np

# Create a dummy audio file for testing
def create_dummy_audio(filename="audio.flac"):
    print(f"Creating dummy audio: {filename}")
    sr = 16000
    duration = 1.0
    # Generate 1 second of silence/noise
    audio = torch.randn(1, int(sr * duration))
    torchaudio.save(filename, audio, sr)
    return filename

filename = "test_audio.flac"
if not os.path.exists(filename):
    create_dummy_audio(filename)

print("Loading model...")
# Load the model
try:
    model = AutoModel.from_pretrained("ai4bharat/indic-conformer-600m-multilingual", trust_remote_code=True)
    if torch.cuda.is_available():
        model = model.cuda()
    print("Model loaded successfully!")
except Exception as e:
    print(f"Model load failed: {e}")
    exit(1)

# Load an audio file
print("Loading audio...")
wav, sr = torchaudio.load(filename)
if wav.shape[0] > 1:
    wav = torch.mean(wav, dim=0, keepdim=True)

target_sample_rate = 16000  # Expected sample rate
if sr != target_sample_rate:
    resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=target_sample_rate)
    wav = resampler(wav)

if torch.cuda.is_available():
    wav = wav.cuda()

# Perform ASR with CTC decoding
print("Running CTC Inference...")
try:
    transcription_ctc = model(wav, "hi", "ctc")
    print("CTC Transcription:", transcription_ctc)
except Exception as e:
    print(f"CTC Inference failed: {e}")

# Perform ASR with RNNT decoding
print("Running RNNT Inference...")
try:
    transcription_rnnt = model(wav, "hi", "rnnt")
    print("RNNT Transcription:", transcription_rnnt)
except Exception as e:
    print(f"RNNT Inference failed: {e}")
