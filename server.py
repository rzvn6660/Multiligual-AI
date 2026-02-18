
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
import soundfile as sf
import logging
import json
from datetime import datetime

# Optimizations for 8GB VRAM
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

# Import our AI providers
# We lazy import them in init_models to ensure server starts even if deps are broken
# from src.asr_provider import SantaliASR
# from src.mt_provider import SantaliTranslator
# from src.tts_provider import SantaliTTS
from src.brain import get_ai_response, FAIL_SAFE_SANTALI

try:
    from src.utils import setup_logger
except ImportError:
    # Fallback logger if util fails
    import logging
    def setup_logger(name):
        l = logging.getLogger(name)
        l.addHandler(logging.StreamHandler())
        l.setLevel(logging.INFO)
        return l


# Initialize App
app = Flask(__name__, static_folder="web/static", template_folder="web/templates")
CORS(app)

logger = setup_logger("WebServer")

# Global Models
asr_model = None
mt_model = None
tts_model = None

# Global Initialization Errors
init_errors = {
    "asr": None,
    "mt": None,
    "tts": None
}

def init_models():
    global asr_model, mt_model, tts_model, init_errors
    logger.info("Initializing Models...")
    
    try:
        from src.asr_provider import SantaliASR
        from src.mt_provider import SantaliTranslator
        from src.tts_provider import SantaliTTS
        
        logger.info("Imports successful, instantiating...")
        
        if not asr_model:
            try:
                asr = SantaliASR()
                if asr.load_model():
                    asr_model = asr
                else:
                    init_errors["asr"] = "Load failed (check logs)"
                    logger.error("ASR Model failed to load.")
            except Exception as e:
                init_errors["asr"] = str(e)
                logger.error(f"ASR Init Error: {e}")
        
        if not mt_model:
            try:
                mt = SantaliTranslator()
                if mt.load_model():
                    mt_model = mt
                else:
                    init_errors["mt"] = "Load failed"
            except Exception as e:
                init_errors["mt"] = str(e)
                logger.error(f"MT Init Error: {e}")

        if not tts_model:
            try:
                tts = SantaliTTS()
                if tts.load_model():
                    tts_model = tts
                else:
                    init_errors["tts"] = "Load failed"
            except Exception as e:
                init_errors["tts"] = str(e)
                logger.error(f"TTS Init Error: {e}")
                
    except Exception as e:
        logger.error(f"CRITICAL: Failed to initialize AI models due to dependency error: {e}")
        init_errors["asr"] = f"Dependency Error: {e}"
        logger.warning("Server will run in text-only/simulation mode if possible.")


# Chat History Management
HISTORY_FILE = "chat_history.json"

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load history: {e}")
        return []

def save_interaction(query_santali, query_english, response_english, response_santali, audio_filename=None):
    history = load_history()
    
    interaction = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "query_santali": query_santali,
        "query_english": query_english,
        "response_english": response_english,
        "response_santali": response_santali,
        "audio_url": f"/api/audio/{audio_filename}" if audio_filename else None
    }
    
    history.append(interaction)
    
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save history: {e}")

@app.route('/api/history', methods=['GET'])
def get_history_route():
    return jsonify(load_history())

@app.route('/api/history', methods=['DELETE'])
def clear_history_route():
    try:
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
            logger.info("Chat history cleared.")
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"Failed to clear history: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        "asr": asr_model is not None and asr_model.model is not None,
        "mt": mt_model is not None and mt_model.model_indic_en is not None and mt_model.model_en_indic is not None,
        "tts": tts_model is not None and tts_model.model is not None,
        "errors": init_errors
    })

@app.route('/api/process', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files['audio']
    mode = request.form.get('mode', 'auto')  # Get User Mode (auto, online, offline)
    
    session_id = str(uuid.uuid4())
    input_filename = f"temp_input_{session_id}.wav"
    output_filename = f"temp_output_{session_id}.wav"
    
    try:
        # Save input audio
        audio_file.save(input_filename)
        
        # --- AUDIO PRE-PROCESSING ---
        ffmpeg_exe = "ffmpeg.exe" if os.path.exists("ffmpeg.exe") else "ffmpeg"
        clean_input_filename = f"clean_input_{session_id}.wav"
        
        # Enhanced FFmpeg command for Noise Cancellation & Cleanup
        # silenceremove: Trims initial silence (start_threshold=-60dB) to avoid processing dead air
        # fast-afftdn: FFT-based Denoising
        # highpass=200: Remove low rumble
        # lowpass=3000: Remove high frequency hiss (speech is mostly < 3kHz)
        # dynaudnorm: Dynamic Audio Normalizer (consistent volume)
        convert_cmd = [
            ffmpeg_exe, "-y",
            "-i", input_filename,
            "-af", "silenceremove=start_periods=1:start_threshold=-60dB:start_duration=0.1s,highpass=f=200,lowpass=f=3000,afftdn=nf=-25,dynaudnorm=f=150:g=15",
            "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
            clean_input_filename
        ]
        
        try:
            import subprocess
            subprocess.check_output(convert_cmd, stderr=subprocess.STDOUT)
            processing_file = clean_input_filename
        except Exception as e:
            logger.error(f"FFmpeg conversion failed: {e}")
            processing_file = input_filename

        # 1. ASR
        logger.info(f"Processing audio: {processing_file} [Mode: {mode}]")
        # Explicitly requesting Santali (sat) to ensure correct model behavior
        santali_query = asr_model.transcribe(processing_file, language='sat')
        logger.info(f"ASR Identified: {santali_query}")
        
        if not santali_query:
            return jsonify({"error": "Could not understand audio"}), 200
            
        # 2. MT (Sat -> Eng)
        # Strict Pipeline: Audio(Sat) -> Text(Sat) -> Text(Eng)
        # User confirmed input is strictly Santali.
        english_query = mt_model.translate(santali_query, src_lang='sat', tgt_lang='eng')
        logger.info(f"MT (Sat->Eng): {english_query}")
        
        # 3. Brain (Gemini/Groq/Ollama)
        # Build context from history
        history_context = []
        try:
            full_history = load_history()
            recent_history = full_history[-5:] if len(full_history) > 5 else full_history
            for item in recent_history:
                history_context.append({"role": "user", "content": item.get("query_english", "")})
                # Strip previous tags if present for context purity
                prev_resp = item.get("response_english", "")
                if "[LLM USED:" in prev_resp:
                    prev_resp = prev_resp.split("[LLM USED:")[0].strip()
                history_context.append({"role": "model", "content": prev_resp})
        except Exception as e:
            logger.warning(f"History error: {e}")

        # Call Brain with Mode (Pass Santali Query for direct FAQ lookup)
        brain_out = get_ai_response(
            text=english_query, 
            santali_text=santali_query, # <--- NEW ARGUMENT
            conversation_history=history_context, 
            mode=mode
        )
        
        if isinstance(brain_out, dict):
            raw_english_response = brain_out.get("text", "")
            source = brain_out.get("source", "UNKNOWN")
            is_fallback = brain_out.get("santali_fallback", False)
        else:
             # Fallback for legacy returns (just in case)
             raw_english_response = str(brain_out)
             source = "UNKNOWN"
             is_fallback = False

        if is_fallback:
             # Case 1: Active Error (Network/AI Fail) -> Use Safety Message
             if source == "FAIL" or source == "EMPTY_INPUT":
                santali_response = FAIL_SAFE_SANTALI
                english_response_tagged = f"System Failure. [ANSWER SOURCE: {source}]" 
             # Case 2: Direct Santali FAQ Hit -> Use DB Text Directly
             elif source == "SQLITE_FAQ":
                santali_response = raw_english_response # Brain returns Santali text in 'text' field for this case
                english_response_tagged = f"[Cached Santali Response] {raw_english_response[:50]}..."
             else:
                # Unknown fallback case
                santali_response = FAIL_SAFE_SANTALI
                english_response_tagged = "Unknown Error."
        else:
            # Normal MT (Eng -> Sat) using clean text
            santali_response = mt_model.translate(raw_english_response, src_lang='eng', tgt_lang='sat')
            english_response_tagged = f"{raw_english_response} [ANSWER SOURCE: {source}]"
        
        logger.info(f"AI Response ({source}): {raw_english_response}")
        
        logger.info(f"Response (Sat): {santali_response}")
        
        # 5. TTS
        audio_path = tts_model.speak_to_file(santali_response, output_filename)
        
        # Construct response
        response_data = {
            "query_santali": santali_query,
            "query_english": english_query,
            "response_english": english_response_tagged, 
            "response_santali": santali_response,
            "llm_source": source
        }
        
        if audio_path and os.path.exists(audio_path):
             response_data["audio_url"] = f"/api/audio/{output_filename}"
        
        # Save to history
        save_interaction(
            santali_query,
            english_query,
            english_response_tagged,
            santali_response,
            output_filename if (audio_path and os.path.exists(audio_path)) else None
        )

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Processing error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(input_filename): os.remove(input_filename)
        if 'clean_input_filename' in locals() and os.path.exists(clean_input_filename): os.remove(clean_input_filename)

@app.route('/api/audio/<filename>')
def get_audio(filename):
    return send_file(filename, mimetype="audio/wav")

if __name__ == "__main__":
    logger.info("--- Server Starting ---")
    try:
        import torch
        import torchvision
        import torchaudio
        logger.info(f"Torch: {torch.__version__}")
        logger.info(f"TorchVision: {torchvision.__version__}")
        logger.info(f"TorchAudio: {torchaudio.__version__}")
        logger.info(f"CUDA Available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            logger.info(f"CUDA Device: {torch.cuda.get_device_name(0)}")
    except ImportError as e:
        logger.error(f"Environment Error: {e}")
        
    init_models()
    # Run on 0.0.0.0 to be accessible
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
