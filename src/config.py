import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ASR
    ASR_MODEL_NAME = "ai4bharat/indic-conformer-600m-multilingual"
    
    # Translation (Sarvam Class)
    # Translation (IndicTrans2)
    MT_MODEL_INDIC_EN = "ai4bharat/indictrans2-indic-en-1B"
    MT_MODEL_EN_INDIC = "ai4bharat/indictrans2-en-indic-1B"
    
    # TTS
    TTS_MODEL_NAME = "ai4bharat/indic-parler-tts"
    
    # Gemini
    GEMINI_MODEL = "gemini-1.5-flash"
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    HF_TOKEN = os.getenv("HF_TOKEN")
    
    # Audio Settings
    SAMPLE_RATE = 16000
