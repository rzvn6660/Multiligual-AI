
# 🎤 TRIEM ASR INPUT PREPROCESSING & OPTIMIZATION

This document outlines 10 key techniques to improve the Audio Input quality for the TRIEM project.
These enhancements ensure that the audio sent to the ASR model (IndicConformer) is clean, normalized, and compatible.

---

## 🚀 1. 16kHz Mono Compatibility
**Goal:** Ensure audio format matches model requirements.
**Implementation:**
- The frontend `script.js` uses `navigator.mediaDevices.getUserMedia` with `{ sampleRate: 16000, channelCount: 1 }`.
- The backend `server.py` uses `ffmpeg` to enforce `-ar 16000 -ac 1`.

## 🤫 2. Silence Detection (Stop Logic)
**Goal:** Automatically stop recording when the user stops speaking.
**Implementation:**
- **Frontend (script.js):** Monitor audio amplitude via `AudioContext`.
- If average volume drops below `SILENCE_THRESHOLD` (e.g., 10) for > 1 second, trigger `stopRecording()`.

## 🗣️ 3. Voice Activity Detection (VAD)
**Goal:** Only process audio segments that contain actual speech.
**Implementation:**
- **FFmpeg Filter:** Use `silenceremove` to strip non-speech segments at start/end.
- **Python:** Use `webrtcvad` (optional future upgrade) or energy-based thresholding in `server.py`.

## 🔊 4. Amplitude Normalization
**Goal:** Ensure consistent volume levels (not too quiet, not too loud).
**Implementation:**
- **FFmpeg Filter:** `dynaudnorm` (Dynamic Audio Normalizer).
- **Command:** `dynaudnorm=f=150:g=15` adapts local gain to target level.

## 🧹 5. Noise Reduction
**Goal:** Remove background hiss, fans, or wind noise.
**Implementation:**
- **Frontend:** `noiseSuppression: true` in `getUserMedia`.
- **Backend:** `afftdn` (FFT-based Denoising) or `highpass=200,lowpass=3000` (Bandpass filter).
- **Explanation:** Human speech is mostly between 200Hz and 3000Hz. Frequencies outside this range are usually noise.

## ✂️ 6. Silence Trimming
**Goal:** Remove dead air from the start and end of the recording.
**Implementation:**
- **FFmpeg Filter:** `silenceremove=start_periods=1:start_threshold=-60dB:start_duration=0.1s`.
- This cuts off initial silence until audio loudness hits -60dB.

## 🌊 7. Chunk-Based Streaming (Ideal State)
**Goal:** Process audio in real-time chunks instead of waiting for the full file.
**Implementation (Conceptual):**
- Use `WebSocket` instead of `POST` requests.
- Stream chunks (20ms-50ms) to backend.
- Feed chunks into ASR model buffer.
- *Current Status:* Batch processing (POST) is simpler and safer for now.

## ⏱️ 8. Audio Duration Logging
**Goal:** Debugging - knowing how much audio we are processing.
**Implementation:**
- **Python:** Use `soundfile` to read frames / sample_rate.
```python
import soundfile as sf
audio = sf.SoundFile('input.wav')
duration = audio.frames / audio.samplerate
logger.info(f"Audio Duration: {duration:.2f}s")
```

## ⚠️ 9. Input Validation (Error Handling)
**Goal:** Prevent crashes from empty or corrupted files.
**Implementation:**
- Check if file size > 0 bytes.
- Check if file format is valid `.wav`.
- Check if duration > min_duration (e.g., 0.5s).
- Return specific error message: "Audio too short" or "File corrupted".

## ⚙️ 10. Configurable Constants
**Goal:** Easy tuning of sensitivity without changing code logic.
**Implementation:**
- Define constants in `src/config_hf.py`:
```python
class Config:
    SAMPLE_RATE = 16000
    SILENCE_THRESHOLD_DB = -60
    MIN_AUDIO_DURATION = 0.5 # seconds
```

---

## ✅ Applied Enhancements in TRIEM
Currently, TRIEM applies:
1.  **Frontend:** 16kHz constraint, Noise Suppression, Echo Cancellation.
2.  **Backend (FFmpeg):** `highpass`, `lowpass`, `afftdn`, `dynaudnorm`, `silenceremove`.
3.  **ASR:** Specific `sat` language flag.

This pipeline ensures that even in noisy tribal environments, the Santali voice input is captured clearly for the AI to understand.
