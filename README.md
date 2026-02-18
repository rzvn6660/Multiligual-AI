# TRIEM AI - Multilingual Tribal Intelligent Assistant

TRIEM AI is an advanced, multilingual voice assistant designed specifically to bridge language barriers for tribal communities, with a primary focus on **Santali**. It leverages state-of-the-art AI models for Automatic Speech Recognition (ASR), Machine Translation (MT), and Text-to-Speech (TTS) to provide a seamless conversational interface.

## 🌟 Key Features

*   **🎙️ Santali Speech Recognition (ASR):** Converts spoken Santali into text using **AI4Bharat's IndicConformer**, robust to noisy environments.
*   **🔄 Bidirectional Translation (MT):** Translates between Santali and English using **AI4Bharat's IndicTrans2**, ensuring high-quality understanding.
*   **🧠 Hybrid Intelligence Engine:**
    *   **Local FAQ Caching:** Instant answers for common questions via SQLite (Offline first).
    *   **Online Intelligence:** Powered by **Groq (Llama 3, Mixtral)** for lightning-fast internet-based queries.
    *   **Fallback Brain:** Uses **Google Gemini 1.5 Flash** or **Ollama** (offline Llama 3) for robust redundancy.
*   **🗣️ Natural Text-to-Speech (TTS):** Responds in natural-sounding Santali using **ParlerTTS**.
*   **🌐 Modern Web Interface:** Clean, responsive Flask-based UI with real-time status indicators and audio visualization.
*   **🖥️ CLI Mode:** Developer-friendly command-line interface for testing and debugging.

---

## 🏗️ Architecture

The system follows a strict processing pipeline:
1.  **Input**: User speaks in Santali (Audio Wav).
2.  **ASR**: Transcribes audio to Santali text (`IndicConformer`).
3.  **MT (Step 1)**: Translates Santali text to English (`IndicTrans2`).
4.  **Intelligence**:
    *   Checks Local FAQ Database.
    *   If not found, queries LLM (Groq/Gemini/Ollama) with English context.
    *   Receives English response.
5.  **MT (Step 2)**: Translates English response back to Santali.
6.  **TTS**: Generates Santali audio from text (`ParlerTTS`).
7.  **Output**: Plays audio response to user.

---

## 🛠️ Prerequisites

To run TRIEM AI effectively, your system should meet the following requirements:

*   **OS:** Windows 10/11 (WSL2 recommended but native Windows supported) or Linux.
*   **Python:** Version 3.10 or higher.
*   **GPU:** NVIDIA GPU with at least **8GB VRAM** (Required for local ASR/MT/TTS models).
*   **Tools:**
    *   **FFmpeg:** Essential for audio processing. Must be installed and added to system PATH.
    *   **CUDA Toolkit:** Compatible with your PyTorch version (e.g., CUDA 11.8 or 12.1).

---

## 🚀 Installation Guide

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/Multilingual-AI.git
cd Multilingual-AI
```

### 2. Set Up Virtual Environment
It is highly recommended to use a virtual environment.
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
This project uses advanced audio libraries. Install PyTorch with CUDA support first.

**Step 3.1: Install PyTorch (CUDA)**
Visit [pytorch.org](https://pytorch.org/) for the command matching your CUDA version. Example for CUDA 11.8:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Step 3.2: Install Project Requirements**
```bash
pip install -r requirements.txt
pip install -r requirements_hf.txt
```
*Note: NeMo Toolkit and ParlerTTS may take some time to compile.*

### 4. Configuration (.env)
Create a `.env` file in the root directory and add your API keys:

```ini
# .env file
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
HF_TOKEN=your_huggingface_write_token

# Optional: Configuration overrides
# OLLAMA_MODEL=llama3
```

---

## 🏃 Usage

### Option 1: One-Click Launcher (Windows)
Double-click the `Start_TRIEM_App.bat` file.
*   It automatically starts the **Flask Backend**.
*   It launches the **Web Interface** in your default browser.

### Option 2: Manual Start (Web Server)
Run the Flask server manually:
```bash
python server.py
```
*   Access the interface at: `http://localhost:5000`

### Option 3: Command Line Interface (CLI)
For testing components without the UI:
```bash
python main_hf.py
```

---

## 📂 Project Structure

```plaintext
Multilingual-AI/
├── src/                    # Core Source Code
│   ├── asr_provider.py     # Speech-to-Text Logic (IndicConformer)
│   ├── mt_provider.py      # Translation Logic (IndicTrans2)
│   ├── tts_provider.py     # Text-to-Speech Logic (ParlerTTS)
│   ├── brain.py            # LLM Intelligence (Groq/Gemini/Ollama)
│   ├── faq_database.py     # SQLite Database Manager
│   └── config_hf.py        # Configuration Settings
├── web/                    # Web Interface
│   ├── static/             # CSS, JS, Images
│   └── templates/          # HTML Templates
├── scripts/                # Utility & Debug Scripts (Recommended location)
├── main_hf.py             # CLI Entry Point
├── server.py              # Flask Web Server
├── requirements.txt       # Basic Dependencies
├── requirements_hf.txt    # Advanced AI Dependencies
└── Start_TRIEM_App.bat    # Windows Launcher
```

---

## 🔧 Troubleshooting

### Common Issues

1.  **`RuntimeError: CUDA out of memory`**
    *   **Cause:** Your GPU VRAM is full.
    *   **Fix:** Close other GPU-intensive apps. Try reducing batch sizes in `src/config_hf.py` if available, or upgrade GPU.

2.  **`FFmpeg not found`**
    *   **Cause:** FFmpeg is not installed or not in PATH.
    *   **Fix:** Download FFmpeg, extract it, and add the `bin` folder to your Windows System Environment Variables "Path".

3.  **`ModuleNotFoundError: No module named 'nemo_toolkit'`**
    *   **Cause:** NeMo installation failed.
    *   **Fix:** NeMo requires `Cython` and specific build tools. Ensure "C++ Build Tools" are installed via Visual Studio Installer.
    *   Try: `pip install cython && pip install nemo_toolkit[all]`

---

## 📜 License
This project is open-source. Models used (IndicConformer, IndicTrans2, ParlerTTS) are subject to their respective licenses from AI4Bharat.

---

## 🙏 Acknowledgements
*   **AI4Bharat** for their groundbreaking Indic models.
*   **Hugging Face** for the model hub infrastructure.
*   **Google DeepMind** & **Meta AI** for LLM capabilities.