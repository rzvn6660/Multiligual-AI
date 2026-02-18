import speech_recognition as sr
from src.utils import setup_logger

logger = setup_logger("AudioInput")

def listen_and_recognize():
    """
    Listens to the microphone and converts speech to text.
    Target language: Santali (sat-IN).
    
    Returns:
        str: The recognized text, or None if failed.
    """
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            logger.info("Adjusting for ambient noise... Please wait.")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            logger.info("Listening... (Speak in Santali)")
            # Listen for up to 10 seconds, with a 5 second pause threshold
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            
            logger.info("Recognizing...")
            # 'sat-IN' is the code for Santali (India)
            text = recognizer.recognize_google(audio, language='sat-IN')
            logger.info(f"Recognized Text: {text}")
            return text
            
    except sr.WaitTimeoutError:
        logger.warning("Listening timed out. No speech detected.")
        return None
    except sr.UnknownValueError:
        logger.warning("Could not understand audio.")
        return None
    except sr.RequestError as e:
        logger.error(f"Could not request results from Google Speech Recognition service; {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None
