from deep_translator import GoogleTranslator
from src.utils import setup_logger

logger = setup_logger("Translation")

def translate_text(text, source_lang='auto', target_lang='en'):
    """
    Translates text from source language to target language.
    
    Args:
        text (str): Text to translate.
        source_lang (str): Source language code (default 'auto', 'sat' for Santali).
        target_lang (str): Target language code (default 'en' for English).
        
    Returns:
        str: Translated text.
    """
    if not text:
        return ""
        
    try:
        # Note: GoogleTranslator usually expects standard ISO codes. 
        # 'sat' is the code for Santali.
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated_text = translator.translate(text)
        
        logger.info(f"Translated '{text}' ({source_lang}) -> '{translated_text}' ({target_lang})")
        return translated_text
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text # Return original text in case of failure to allow flow to continue (optimistic)
