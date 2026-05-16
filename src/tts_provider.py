import torch
import numpy as np
import re
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf
from src.utils import setup_logger
from src.config import Config

logger = setup_logger("TTS_Provider")

class SantaliTTS:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
    def load_model(self):
        try:
            logger.info(f"Loading TTS Model: {Config.TTS_MODEL_NAME} on {self.device}...")
            
            self.model = ParlerTTSForConditionalGeneration.from_pretrained(
                Config.TTS_MODEL_NAME,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                low_cpu_mem_usage=True
            ).to(self.device)
            self.tokenizer = AutoTokenizer.from_pretrained(Config.TTS_MODEL_NAME)
            
            logger.info("TTS Model loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to load TTS model: {e}")
            return False

    def speak_to_file(self, text, output_file="response.wav"):
        """
        Generates audio for the text and saves to file.
        For Santali, we need to provide a description prompt that specifies the language.
        """
        if not self.model:
            return None
            
        try:
            # Chunking Best Practice (Split into sentences, 2-3 per chunk)
            clean_text = text.replace('\n', ' ').strip()
            
            # Split chunks by punctuation
            raw_sentences = re.split(r'([.,?!᱾])', clean_text)
            
            sentences = []
            for i in range(0, len(raw_sentences)-1, 2):
                if raw_sentences[i].strip():
                    sentences.append((raw_sentences[i] + raw_sentences[i+1]).strip())
            
            if len(raw_sentences) % 2 == 1 and raw_sentences[-1].strip():
                sentences.append(raw_sentences[-1].strip())
            
            if not sentences:
                sentences = [clean_text]
                
            chunks = []
            current_chunk = []
            
            for sentence in sentences:
                current_chunk.append(sentence)
                if len(current_chunk) >= 2: # 2 sentences per chunk
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    
            if current_chunk:
                chunks.append(" ".join(current_chunk))

            description = "A female speaker delivers a very slow, clearly articulated, and high-quality speech in Santali."
            input_ids = self.tokenizer(description, return_tensors="pt").input_ids.to(self.device)
            attention_mask = torch.ones_like(input_ids)
            
            audio_arrays = []
            sample_rate = getattr(self.model.config, "sampling_rate", 44100) # fallback
            if hasattr(self.model.config, "audio_encoder") and hasattr(self.model.config.audio_encoder, "sampling_rate"):
                 sample_rate = self.model.config.audio_encoder.sampling_rate
                 
            pause_array = np.zeros(int(sample_rate * 0.5), dtype=np.float32) # 500ms pause <break time="500ms"/>

            for chunk in chunks:
                if not chunk.strip(): continue
                logger.info(f"Generating audio for chunk: {chunk}")
                prompt_input_ids = self.tokenizer(chunk, return_tensors="pt").input_ids.to(self.device)
                prompt_attention_mask = torch.ones_like(prompt_input_ids)

                generation = self.model.generate(
                    input_ids=input_ids, 
                    prompt_input_ids=prompt_input_ids,
                    attention_mask=attention_mask,
                    prompt_attention_mask=prompt_attention_mask
                )
                audio_arr = generation.float().cpu().numpy().squeeze()
                
                # Check for rate control: The user mentioned "rate = 0.85". 
                # Implementing simple time-stretching with numpy is complex without specialized libraries, 
                # but we can rely on ParlerTTS's description. The prompt "delivers a very slow... speech" helps.
                if audio_arrays: # Add SSML-like 500ms pause before next chunk
                    audio_arrays.append(pause_array)
                audio_arrays.append(audio_arr)
            
            if not audio_arrays:
                return None
                
            final_audio = np.concatenate(audio_arrays)
            
            # Save
            sf.write(output_file, final_audio, sample_rate)
            logger.info(f"Chunked Audio saved to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"TTS Generation error: {e}")
            return None

if __name__ == "__main__":
    tts = SantaliTTS()
    # tts.load_model()
