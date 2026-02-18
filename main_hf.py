import sys
import time
import os
import wave
import pyaudio

# NEW Providers
from src.asr_provider import SantaliASR
from src.mt_provider import SantaliTranslator
from src.tts_provider import SantaliTTS
from src.brain import get_gemini_response
from src.utils import setup_logger

logger = setup_logger("Main_Advanced")

def record_audio(filename="input.wav", duration=5):
    """
    Simple recorder for testing since we need a file for NeMo.
    """
    chunk = 1024
    format = pyaudio.paInt16
    channels = 1
    rate = 16000 # NeMo often needs 16kHz
    
    p = pyaudio.PyAudio()
    
    print(f"Recording for {duration} seconds... Speak now!")
    stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
    
    frames = []
    
    for i in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)
        
    print("Recording stopped.")
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    return filename

def play_audio(filename):
    try:
        os.startfile(filename) 
        # or use playsound, but os.startfile is reliable on Windows for default player
    except Exception as e:
        logger.error(f"Playback error: {e}")

def main():
    logger.info("Initializing Advanced Santali AI Assistant (HF/NeMo/Sarvam)...")
    logger.warning("This mode requires heavy models. Loading may take time...")
    
    # 1. Load Models (Lazy loading is better but we load upfront to check issues)
    asr = SantaliASR()
    if not asr.load_model():
        logger.error("ASR Model failed. Exiting.")
        return

    mt = SantaliTranslator()
    if not mt.load_model():
        logger.error("MT Model failed. Exiting.")
        return

    tts = SantaliTTS()
    if not tts.load_model():
        logger.error("TTS Model failed. Exiting.")
        return

    logger.info("All Systems GO! Ctrl+C to exit.")
    
    try:
        while True:
            input("\nPress Enter to start recording (5s)...")
            
            # 1. Listen (Record -> Transcribe)
            audio_file = record_audio()
            santali_text = asr.transcribe(audio_file)
            
            if not santali_text:
                print("Could not understand audio.")
                continue
                
            print(f"-- Recognized: {santali_text}")
                
            # 2. Translate to English
            english_query = mt.translate(santali_text, src_lang='sat', tgt_lang='eng')
            print(f"-- English Query: {english_query}")
            
            if not english_query: continue
                
            # 3. Ask Gemini
            english_response = get_gemini_response(english_query)
            print(f"-- Gemini: {english_response}")
            
            if not english_response: continue
                
            # 4. Translate back to Santali
            santali_response = mt.translate(english_response, src_lang='eng', tgt_lang='sat')
            print(f"-- Santali Response: {santali_response}")
            
            # 5. Speak
            output_file = tts.speak_to_file(santali_response)
            if output_file:
                play_audio(output_file)
            
    except KeyboardInterrupt:
        logger.info("Exiting...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal Error: {e}")

if __name__ == "__main__":
    main()
