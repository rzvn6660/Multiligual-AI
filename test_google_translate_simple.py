
from deep_translator import GoogleTranslator
from deep_translator.constants import GOOGLE_LANGUAGES_TO_CODES
import sys

# Manually add Santali to the supported languages
GOOGLE_LANGUAGES_TO_CODES['santali'] = 'sat'

def reconfigure_stdout():
    """Reconfigure stdout/stderr to use utf-8 if possible."""
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass # Python < 3.7 or other environments where reconfigure is not available

def test_google_translate_patched():
    reconfigure_stdout()
    print("--- Testing Google Translate (Santali <-> English) ---")
    
    # Use a file for output as a reliable fallback for intricate scripts
    with open("test_translation_result.txt", "w", encoding="utf-8") as f:
        f.write(f"--- Testing Google Translate (Santali <-> English) ---\n")
        
        # 1. Santali (sat) to English (en)
        santali_text = "ᱡᱚᱦᱟᱨ ᱥᱟᱹᱜᱩᱱ ᱥᱮᱛᱟᱜ" 
        
        try:
            msg_header = "\n[Santali -> English]"
            msg_original = f"Original: {santali_text}"
            
            print(msg_header)
            print(msg_original)
            f.write(msg_header + "\n")
            f.write(msg_original + "\n")
            
            # Initialize translator with the updated languages dict passed explicitly
            translator_sat_to_en = GoogleTranslator(source='santali', target='en', languages=GOOGLE_LANGUAGES_TO_CODES)
            translated_en = translator_sat_to_en.translate(santali_text)
            
            res_msg = f"Translated: {translated_en}"
            print(res_msg)
            f.write(res_msg + "\n")
            
        except Exception as e:
            err_msg = f"Error translating to English: {e}"
            print(err_msg)
            f.write(err_msg + "\n")

        # 2. English (en) to Santali (sat)
        english_text = "Hello, I am testing this translation system."
        
        try:
            msg_header = "\n[English -> Santali]"
            msg_original = f"Original: {english_text}"
            
            print(msg_header)
            print(msg_original)
            f.write(msg_header + "\n")
            f.write(msg_original + "\n")
            
            # Initialize translator
            translator_en_to_sat = GoogleTranslator(source='en', target='santali', languages=GOOGLE_LANGUAGES_TO_CODES)
            translated_sat = translator_en_to_sat.translate(english_text)
            
            res_msg = f"Translated: {translated_sat}"
            try:
                print(res_msg)
            except UnicodeEncodeError:
                print("Translated: [Output contains characters not supported by console encoding. See test_translation_result.txt]")
            f.write(res_msg + "\n")
            
        except Exception as e:
            err_msg = f"Error translating to Santali: {e}"
            print(err_msg)
            f.write(err_msg + "\n")

    print("\nCheck 'test_translation_result.txt' if console output is garbled.")

if __name__ == "__main__":
    test_google_translate_patched()
