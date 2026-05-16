import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransToolkit.processor import IndicProcessor
from src.utils import setup_logger
from src.config import Config

logger = setup_logger("MT_Provider")

class SantaliTranslator:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.ip = None
        
        # Indic -> En components
        self.tokenizer_indic_en = None
        self.model_indic_en = None
        
        # En -> Indic components
        self.tokenizer_en_indic = None
        self.model_en_indic = None

    def load_model(self):
        try:
            logger.info("Initializing IndicTrans2 System...")
            
            # Initialize Processor (handles both directions)
            self.ip = IndicProcessor(inference=True)
            
            # 1. Load Indic -> English Model
            logger.info(f"Loading Indic-En Model: {Config.MT_MODEL_INDIC_EN}")
            self.tokenizer_indic_en = AutoTokenizer.from_pretrained(Config.MT_MODEL_INDIC_EN, trust_remote_code=True)
            self.model_indic_en = AutoModelForSeq2SeqLM.from_pretrained(
                Config.MT_MODEL_INDIC_EN, 
                trust_remote_code=True, 
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            ).to(self.device)
            self.model_indic_en.eval()

            # 2. Load English -> Indic Model
            logger.info(f"Loading En-Indic Model: {Config.MT_MODEL_EN_INDIC}")
            self.tokenizer_en_indic = AutoTokenizer.from_pretrained(Config.MT_MODEL_EN_INDIC, trust_remote_code=True)
            self.model_en_indic = AutoModelForSeq2SeqLM.from_pretrained(
                Config.MT_MODEL_EN_INDIC, 
                trust_remote_code=True, 
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            ).to(self.device)
            self.model_en_indic.eval()
            
            logger.info("IndicTrans2 Models loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to load MT models: {e}")
            return False


    def translate(self, text, src_lang, tgt_lang, model_type="indictrans2"):
        """
        Translates text using either IndicTrans2 or Google Translate.
        model_type: 'indictrans2' (Offline/Local) or 'google' (Online)
        """
        if not text or not text.strip():
            return ""

        if model_type == "google":
             from deep_translator import GoogleTranslator
             from deep_translator.constants import GOOGLE_LANGUAGES_TO_CODES
             GOOGLE_LANGUAGES_TO_CODES['santali'] = 'sat'
             
             # STRICT PIPELINE ENFORCEMENT FOR GOOGLE TRANSLATE
             # 1. Santali -> English (for Brain Input)
             # 2. English -> Santali (for TTS Output)
             
             def map_google_code(lang):
                 if lang == 'sat': return 'santali'
                 if lang == 'eng': return 'en'
                 # Fallback for others (though not used in this specific pipeline)
                 return lang

             s_lang = map_google_code(src_lang)
             t_lang = map_google_code(tgt_lang)
             
             # Validation: Ensure we are only doing Sat<->En
             valid_pair = (s_lang == 'santali' and t_lang == 'en') or (s_lang == 'en' and t_lang == 'santali')
             
             if not valid_pair:
                 logger.warning(f"Google Translate requested for non-standard pair: {s_lang} -> {t_lang}. Proceeding, but this is outside the primary Santali pipeline.")

             logger.info(f"Google MT Pipeline: '{text[:20]}...' [{s_lang.upper()} -> {t_lang.upper()}]")
             try:
                 translator = GoogleTranslator(source=s_lang, target=t_lang)
                 return translator.translate(text)
             except Exception as e:
                 logger.error(f"Google Translation error: {e}")
                 return text

        # --- IndicTrans2 (Default) ---
        
        # Map simple codes to IndicTrans2 ISO codes
        # Santali Latin/OlChiki handling: usually TTS/ASR uses one, MT might expect specific script.
        # IndicTrans2 expects 'sat_Olck' for Santali.
        code_map = {
            'eng': 'eng_Latn',
            'sat': 'sat_Olck',
            'hi': 'hin_Deva',
            'bn': 'ben_Beng'
        }
        
        src_iso = code_map.get(src_lang, src_lang)
        tgt_iso = code_map.get(tgt_lang, tgt_lang)
        
        try:
            # Select Direction & Model
            if src_lang == 'eng':
                # English -> Indic
                model = self.model_en_indic
                tokenizer = self.tokenizer_en_indic
            else:
                # Indic -> English (or Indic-Indic if supported, assuming Indic-En here)
                model = self.model_indic_en
                tokenizer = self.tokenizer_indic_en
            
            if not model:
                logger.error("Model not loaded for this direction.")
                return text

            # logging
            logger.info(f"Translating via IndicTrans2: '{text}' ({src_iso} -> {tgt_iso})")

            # 1. Preprocess Batch
            batch = self.ip.preprocess_batch(
                [text],
                src_lang=src_iso,
                tgt_lang=tgt_iso
            )
            
            # 2. Tokenize
            inputs = tokenizer(
                batch,
                truncation=True,
                padding="longest",
                return_tensors="pt",
                return_attention_mask=True,
            ).to(self.device)
            
            # 3. Generate
            with torch.no_grad():
                generated_tokens = model.generate(
                    **inputs,
                    use_cache=True,
                    min_length=0,
                    max_length=256,
                    num_beams=5,
                    num_return_sequences=1,
                )
            
            # 4. Decode
            decoded = tokenizer.batch_decode(
                generated_tokens,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True,
            )
            
            # 5. Postprocess
            translations = self.ip.postprocess_batch(decoded, lang=tgt_iso)
            final_text = translations[0]
            
            # Clean up potential tokenization artifacts if postprocess misses any
            # (Though IP usually handles this well)
            
            logger.info(f"Translated: {final_text}")
            return final_text
            
        except Exception as e:
            logger.error(f"Translation Error: {e}")
            return text

if __name__ == "__main__":
    pass
