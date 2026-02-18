
# TRIEM AI - Code Explanation Guide 🎓

This document explains every part of the **TRIEM (Tribal Responsive Intelligent Empowerment Model)** project. It is written in simple English to help you understand the code structure, functions, and logic for your presentation or viva.

---

## 📂 Project Structure Overview

Think of this project like a **human body**:

*   **`server.py` (The Heart):** Manages everything, receives requests, and coordinates actions.
*   **`src/brain.py` (The Brain):** Thinks, decides what to say, and uses AI models (Groq/Gemini).
*   **`src/asr_provider.py` (The Ears):** Listens to audio and converts it to text (ASR).
*   **`src/tts_provider.py` (The Mouth):** Converts text responses back into speech (TTS).
*   **`src/mt_provider.py` (The Translator):** Translates between Santali and English.
*   **`web/` (The Face):** What the user sees and interacts with (HTML/CSS/JS).

---

## 1. `server.py` (The Main Controller)

### 🟢 Purpose
This is the **Flask Web Server**. It acts as the bridge between the user's browser and the AI models. When you click "Record" or "Upload", this file receives the audio and manages the entire pipeline.

### 🔗 Imports
*   `flask`: To create the web server.
*   `soundfile`, `os`: To handle audio files.
*   `src.brain`, `src.asr_provider`, etc.: Imports our custom AI modules.

### ⚙️ Main Functions

#### `init_models()`
*   **What it does:** Starts up all the AI engines (ASR, Translate, TTS) when the app launches.
*   **Why important:** Without this, the app is "brain dead" and can't process anything.

#### `process_audio()` (The Most Important Function!)
*   **What it does:** This is the **Master Pipeline**.
    1.  **Receives Audio:** Takes the user's voice file.
    2.  **Cleans Audio:** Uses FFmpeg to remove background noise.
    3.  **ASR (Listen):** Converts Santali Audio -> Santali Text.
    4.  **MT (Translate):** Converts Santali Text -> English Text.
    5.  **Brain (Think):** Sends English Text to AI (Brain) to get an answer.
    6.  **MT (Translate Back):** Converts English Answer -> Santali Answer.
    7.  **TTS (Speak):** Converts Santali Answer -> Audio.
*   **Input:** Audio File (`.wav`).
*   **Output:** JSON data containing the text and the path to the response audio.

#### `save_interaction()`
*   **What it does:** Saves the chat (Question & Answer) to `chat_history.json`.
*   **Why important:** Allows the user to see their past conversations.

### 📝 Key Code Explanation
```python
# This line ensures we use the best available device (GPU if possible) for PyTorch
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
```

---

## 2. `src/brain.py` (The Intelligence)

### 🟢 Purpose
This file decides **what to say**. It connects to advanced AI models (like Google Gemini or Groq) to generate smart answers. It also handles the **offline/online** logic.

### 🔗 Imports
*   `groq`: For ultra-fast online AI responses.
*   `google.genai`: For Google Gemini AI (backup).
*   `src.faq_database`: To check if we already know the answer.

### ⚙️ Main Functions

#### `get_ai_response(text, santali_text, ...)`
*   **What it does:** The core thinking function.
*   **Logic Flow:**
    1.  **Check FAQ:** "Have I answered this before?" If yes, return the saved answer instantly (High Speed!).
    2.  **Check Internet:** If online, try **Groq** (Fastest AI).
    3.  **Fallback:** If Groq fails, try **Gemini** or **Ollama** (Offline).
*   **Input:** User's text (in English and Santali).
*   **Output:** The smartest answer the AI can generate.

#### `normalize_text(text)`
*   **What it does:** Cleans up text by removing weird symbols.
*   **Why:** Helps the computer match questions better (e.g., "Hello!" becomes "hello").

---

## 3. `src/config_hf.py` (The Settings)

### 🟢 Purpose
This is a **configuration file**. It stores "hard-coded" settings like Model Names, API Keys (loaded securely), and Audio Settings.

### 📝 Key Code
```python
# These are the specific Hugging Face models we use for Santali
ASR_MODEL_NAME = "ai4bharat/indic-conformer-600m-multilingual"
TTS_MODEL_NAME = "ai4bharat/indic-parler-tts"
```
*   **Why important:** If we want to change the AI model later, we only change it here, not everywhere in the code.

---

## 4. `src/asr_provider.py` (The Ears 👂)

### 🟢 Purpose
**ASR = Automatic Speech Recognition**. This file converts spoken Santali audio into written Santali text.

### ⚙️ Main Functions

#### `transcribe(audio_file_path)`
*   **What it does:** Loads the audio, sends it to the `IndicConformer` model, and returns the text.
*   **Technical Detail:** It resamples audio to 16,000 Hz because that's what the AI expects.

---

## 5. `src/mt_provider.py` (The Translator 🔄)

### 🟢 Purpose
**MT = Machine Translation**. Since most smart AIs understand English best, we translate Santali to English to "think", and then translate the answer back to Santali.

### ⚙️ Main Functions

#### `translate(text, src_lang, tgt_lang)`
*   **What it does:** Translates text from Source Language -> Target Language.
*   **Input:** Text, e.g., "Johar" (Santali).
*   **Output:** Translated Text, e.g., "Hello" (English).
*   **Key Logic:** It uses `ai4bharat/indictrans2` models which are state-of-the-art for Indian languages.

---

## 6. `src/tts_provider.py` (The Mouth 🗣️)

### 🟢 Purpose
**TTS = Text to Speech**. This file takes the final Santali text answer and turns it into a human-like voice.

### ⚙️ Main Functions

#### `speak_to_file(text)`
*   **What it does:** Uses the `ParlerTTS` model to generate audio.
*   **Why important:** It allows the tribal user (who might not read) to **hear** the answer.
*   **Special Trick:** It uses a "description" prompt ("A female speaker...") to control how the voice sounds.

---

## 7. `src/faq_database.py` (The Memory 🧠)

### 🟢 Purpose
This is a **Local Cache**. It remembers questions and answers using a simple database (`SQLite`).

### ⚙️ Main Functions

#### `get_answer(question)`
*   **What it does:** Searches the database.
*   **Fuzzy Matching:** It uses `difflib` to find answers even if the question is slightly different (e.g., "What is your name?" vs "What's ur name?").

#### `add_entry(question, answer)`
*   **What it does:** Saves a new Q/A pair to the database so the AI learns and gets faster next time.

---

## 8. Web Interface Files (The Face 🖥️)

### `web/templates/index.html`
*   **Purpose:** The **Skeleton** of the website.
*   **Contains:** The Record button, Chat window, Visualizer canvas, and Dropdowns.
*   **Key Element:** `<canvas id="visualizer">` - This creates the cool audio wave animation.

### `web/static/style.css`
*   **Purpose:** The **Makeup** (Design).
*   **Features:**
    *   **Glassmorphism:** The inputs look like frosted glass (`backdrop-filter: blur`).
    *   **Animations:** The pulsing ring around the record button.
    *   **Responsive:** Makes sure it looks good on mobile and PC.

### `web/static/script.js`
*   **Purpose:** The **Muscles** (Action).
*   **Key Logic:**
    *   **`startRecording()`**: Asks browser for microphone access and starts recording.
    *   **`sendAudioToBackend()`**: Sends the recorded blob to `server.py` and waits for the result.
    *   **`drawVisualizer()`**: Draws the dancing bars based on voice volume.
    *   **`updateInputMode()`**: Switches between "Microphone" and "File Upload" modes.

---

## 9. Helper Files

### `Start_TRIEM_App.bat`
*   **Purpose:** A one-click launcher for Windows. You double-click this, and it opens the server and browser automatically.

### `requirements.txt` / `requirements_hf.txt`
*   **Purpose:** A shopping list for Python. It tells the computer which libraries (like `torch`, `flask`, `transformers`) need to be installed for the code to run.

---

## 🌟 Summary of the Flow

1.  **User** speaks into the **Browser** (`script.js`).
2.  **Server** (`server.py`) gets the audio.
3.  **ASR** (`asr_provider.py`) types it out.
4.  **MT** (`mt_provider.py`) translates to English.
5.  **Brain** (`brain.py`) thinks of an answer.
6.  **MT** translates answer back to Santali.
7.  **TTS** (`tts_provider.py`) speaks the answer.
8.  **User** hears the response!

This structure ensures the AI is **Modular** (easy to fix parts separately) and **Scalable** (can add more languages later).
