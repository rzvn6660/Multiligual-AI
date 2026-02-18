# Setup Guide for Santali Voice AI (Advanced)

This version uses high-performance models from AI4Bharat and Sarvam AI. These models are large and require significant computational power (GPU recommended).

## Prerequisites
- **NVIDIA GPU** (Recommended: 8GB+ VRAM). Running on CPU will be extremely slow.
- **Python 3.10+**
- **Git** installed and added to PATH.

## Model Details
- **ASR**: `ai4bharat/indicconformer_stt_sat_hybrid_ctc_rnnt_large` (Hybrid CTC-RNNT Conformer)
- **MT**: `sarvamai/sarvam-translate` (LLM based Translation) or `ai4bharat/IndicTrans2`
- **TTS**: `ai4bharat/indic-parler-tts` (Parler TTS)
- **LLM**: Google Gemini (via API)

## Installation Instructions

### IMPORTANT: Model Access
The **IndicConformer** model is **GATED**. You must:
1.  Create a Hugging Face account.
2.  Go to [ai4bharat/indicconformer_stt_sat_hybrid_rnnt_large](https://huggingface.co/ai4bharat/indicconformer_stt_sat_hybrid_rnnt_large) and accept the terms of use.
3.  Get an Access Token (Settings -> Access Tokens -> New Token).
4.  Add the token to your `.env` file:
    ```
    HF_TOKEN=hf_...
    ```

1.  **Install PyTorch with CUDA**:
    Your CUDA 12.6 driver is excellent. It is backward compatible with PyTorch's CUDA 12.4 builds.
    Run this command:
    ```bash
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
    ```

2.  **Install NeMo Toolkit**:
    NeMo is required for the ASR model.
    ```bash
    pip install nemo_toolkit['asr']
    ```
    *Note: On Windows, NeMo installation can be tricky. You might need to install `Cython` and a C++ compiler (Visual Studio Build Tools).*

3.  **Install Other Dependencies**:
    ```bash
    pip install -r requirements_hf.txt
    ```

## Usage

Run the advanced pipeline:
```bash
python main_hf.py
```

## Troubleshooting
- **ASR Errors**: If NeMo fails to load, ensure you have the correct PyTorch version and C++ build tools.
- **Memory Errors**: If you get OOM (Out of Memory), try running on a machine with a larger GPU or use the smaller component scripts individually.
