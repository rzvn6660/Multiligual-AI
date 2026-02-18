from gtts import gTTS
import os
import tempfile
import time
from playsound import playsound
from src.utils import setup_logger

logger = setup_logger("AudioOutput")

def speak_text(text, lang='sat'):
    """
    Converts text to speech and plays it.
    
    Args:
        text (str): Text to speak.
        lang (str): Language code (default 'sat').
    """
    if not text:
        return

    try:
        logger.info(f"Generating TTS for: {text} (lang={lang})")
        
        # Create a temporary file
        # suffix .mp3 is important for gTTS
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd) # Close the file descriptor immediately so gTTS can write to it
        
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(path)
        
        logger.info("Playing audio...")
        # playsound depends on the platform. 1.2.2 is usually good on Windows.
        try:
             playsound(path)
        except Exception as ps_error:
             logger.error(f"playsound failed: {ps_error}. Trying os.startfile...")
             # Fallback for Windows
             try:
                 os.startfile(path)
                 # Give it some time to play since startfile is non-blocking usually
                 # This is a bit hacky but better than silence in a demo
                 time.sleep(5) 
             except Exception as os_error:
                 logger.error(f"Falback playback failed: {os_error}")

    except Exception as e:
        logger.error(f"TTS Error: {e}")
        
    finally:
        # Cleanup
        try:
            if os.path.exists(path):
                # playsound 1.2.2 doesn't always release the file immediately
                # Simple retry mechanism for deletion or just ignore if it fails in a temp dir
                try:
                    os.remove(path)
                except PermissionError:
                    logger.warning(f"Could not remove temp file {path} (in use). It will persist in temp.")
        except UnboundLocalError:
            pass
