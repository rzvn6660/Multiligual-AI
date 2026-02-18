
# 🎤 TRIEM AI - Viva Presentation Script & Code Walkthrough

**Use this script during your presentation. It is structured to help you explain the code line-by-line or block-by-block to the examiner.**

---

## 🟢 Introduction (Opening Statement)

"Good morning/afternoon. My project is **TRIEM AI** (Tribal Responsive Intelligent Empowerment Model).
It is a **Voice-to-Voice AI Assistant** specifically designed for the **Santali language**.
Unlike generic assistants, TRIEM focuses on:
1.  **Local Language Support:** Understanding Santali using AI4Bharat models.
2.  **Hybrid Intelligence:** Working both **Online** (Groq/Gemini) and **Offline** (Ollama/Local Cache).
3.  **Empowerment:** Helping tribal communities access information through simple voice interaction."

---

## 🏗️ Architecture Overview (The "Body" Analogy)

"Before I show the code, I want to explain how the system works. I designed it like a human body:
*   **The Ears (`asr_provider.py`):** Listens to Santali audio.
*   **The Brain (`brain.py`):** Thinks and generates answers.
*   **The Mouth (`tts_provider.py`):** Speaks the answer back.
*   **The Translator (`mt_provider.py`):** Translates Santali to English (for thinking) and back.
*   **The Heart (`server.py`):** Connects everything together."

---

## 💻 Code Walkthrough (Detailed Explanation)

*(Open `server.py` on your screen)*

### 1. `server.py` - The Main Controller

"This is the main entry point. It's a **Flask** web server."

**Key Lines to Point At:**

`app = Flask(__name__, ...)`
> "Here, I initialize the web application. `static_folder` serves my CSS/JS, and `template_folder` serves the HTML."

`def init_models():`
> "This function runs when the app starts. It loads our heavy AI models into memory **once** so we don't reload them for every request. This makes the app faster."

`@app.route('/api/process', methods=['POST'])`
> "This is the most important endpoint. It receives the user's audio file from the frontend."

`def process_audio():`
> "Let me explain the pipeline inside this function step-by-step:
> 1. **Data Collection:** I get `request.files['audio']`.
> 2. **ASR:** I call `asr_model.transcribe()` to get the text from audio.
> 3. **Translation:** I call `mt_model.translate()` to convert Santali to English.
> 4. **Intelligence:** I send the English text to `get_ai_response()` (The Brain).
> 5. **Response:** The AI gives an answer.
> 6. **Translation Back:** I translate the English answer back to Santali.
> 7. **TTS:** Finally, `tts_model.speak_to_file()` converts that text into an audio file for the user to hear."

---

*(Open `src/brain.py`)*

### 2. `src/brain.py` - The Intelligence Engine

"This file decides *what* to say. It handles the logic for Online vs. Offline modes."

**Key Lines to Point At:**

`faq_manager = FAQManager()`
> "I initialize a local database manager here. This is my **Cache Memory**."

`def get_ai_response(text, ...):`
> "This function takes the user's query and finds the best answer."

`(Line ~86) if santali_text: ... faq_manager.get_answer()`
> "First, I check if we already have the answer in our local database. If yes, I return it immediately. This is **zero-latency** and works offline!"

`(Line ~128) use_groq = mode in ["auto", "online"] ...`
> "If we are online, I use **Groq**. It's an ultra-fast AI inference engine."

`(Line ~161) if mode in ["auto", "offline"]: ...`
> "If internet fails or if the user selected 'Offline Mode', I switch to **Ollama**. This runs a localized Llama-3 model directly on this laptop, ensuring privacy and reliability."

---

*(Open `src/asr_provider.py`)*

### 3. `src/asr_provider.py` - The ASR Module

"This module handles speech recognition using the **IndicConformer** model."

**Key Lines to Point At:**

`self.model = AutoModel.from_pretrained(Config.ASR_MODEL_NAME ...)`
> "I am using the **Hugging Face `transformers`** library to load the model defined in my config file."

`wav, sr = torchaudio.load(audio_file_path)`
> "I use **TorchAudio** to load the .wav file. I also resample it to 16kHz because that is what the AI model requires."

`transcription = self.model(wav, language='sat')`
> "This is the actual inference. I explicitly pass `language='sat'` to tell the model to listen for **Santali** specifically."

---

*(Open `src/mt_provider.py`)*

### 4. `src/mt_provider.py` - The Translator

"Since most large AI models understand English best, translation is crucial."

**Key Lines to Point At:**

`self.ip = IndicProcessor(inference=True)`
> "I use **IndicTransToolkit**. It handles the complex script issues often found in Indian languages like Santali (Ol Chiki script)."

`batch = self.ip.preprocess_batch( ... src_lang='sat_Olck', tgt_lang='eng_Latn')`
> "Here, I prepare the text. notice the codes: `sat_Olck` stands for Santali in Ol Chiki script. `eng_Latn` is English."

`model.generate(**inputs ...)`
> "The model then predicts the translated sentence."

---

*(Open `src/tts_provider.py`)*

### 5. `src/tts_provider.py` - The Text-to-Speech

"This gives the AI a voice."

**Key Lines to Point At:**

`description = "A female speaker delivers a very slow ... in Santali."`
> "I am using **ParlerTTS**. It is a unique model that takes a *text description* of the voice. I programmed it to speak slowly and clearly so tribal users can understand easily."

`sf.write(output_file, audio_arr ...)`
> "Finally, I save the generated sound wave as a `.wav` file, which is sent back to the user's browser."

---

*(Open `web/static/script.js`)*

### 6. The Frontend Logic (`script.js`)

"This JavaScript file makes the website interactive."

**Key Functions:**

`navigator.mediaDevices.getUserMedia({ audio: true })`
> "This line asks the browser for permission to use the microphone."

`mediaRecorder.ondataavailable`
> "As the user speaks, we collect the audio data into chunks."

`drawVisualizer()`
> "This function draws the real-time audio wave animation you see on screen using the HTML5 Canvas API."

---

## 🏁 Conclusion

"To summarize:
1.  **Frontend** captures audio.
2.  **Server** orchestrates the process.
3.  **ASR/MT/TTS** models handle the language barriers.
4.  **Brain** provides the intelligence via Hybrid Cloud/Local AI.

This architecture ensures TRIEM is **Robust**, **Scalable**, and **Culturally Responsive**. Thank you!"
