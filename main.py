import os
import sys
import time
from dotenv import load_dotenv

from src.audio_input import listen_and_recognize
from src.translation import translate_text
from src.brain import get_gemini_response
from src.audio_output import speak_text
from src.utils import setup_logger

logger = setup_logger("Main")

def main():
    logger.info("Starting Santali AI Assistant...")
    
    # Check for API Key
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("CRITICAL: GEMINI_API_KEY is not set in .env file.")
        print("\n\n!! PLEASE SET YOUR GEMINI_API_KEY IN THE .env FILE !!\n\n")
        return

    logger.info("System Ready. Ctrl+C to exit.")
    
    try:
        while True:
            print("\n" + "="*50)
            print("Say something in Santali...")
            print("="*50 + "\n")
            
            # 1. Listen (Santali)
            santali_text = listen_and_recognize()
            if not santali_text:
                continue # Retry listening
                
            # 2. Translate to English
            english_query = translate_text(santali_text, source_lang='sat', target_lang='en')
            if not english_query:
                logger.warning("Translation failed. Skipping.")
                continue
                
            # 3. Ask Gemini Integration
            english_response = get_gemini_response(english_query)
            if not english_response:
                logger.warning("No response from AI.")
                continue
                
            # 4. Translate back to Santali
            santali_response = translate_text(english_response, source_lang='en', target_lang='sat')
            logger.info(f"Santali Response: {santali_response}")
            
            # 5. Speak (Santali)
            speak_text(santali_response, lang='sat')
            
            # Small pause between turns
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Exiting...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal Error: {e}")

if __name__ == "__main__":
    main()
