import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf
from src.utils import setup_logger
from src.config_hf import Config

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
            # Prompt construction for Parler TTS
            # Enhanced description for better clarity and loudness
            description = "A female speaker delivers a very slow, clearly articulated, and high-quality speech in Santali."
            
            input_ids = self.tokenizer(description, return_tensors="pt").input_ids.to(self.device)
            prompt_input_ids = self.tokenizer(text, return_tensors="pt").input_ids.to(self.device)
            
            # Create attention masks manually to ensure reliability
            attention_mask = torch.ones_like(input_ids)
            prompt_attention_mask = torch.ones_like(prompt_input_ids)

            generation = self.model.generate(
                input_ids=input_ids, 
                prompt_input_ids=prompt_input_ids,
                attention_mask=attention_mask,
                prompt_attention_mask=prompt_attention_mask
            )
            # Ensure float32 for audio processing
            audio_arr = generation.float().cpu().numpy().squeeze()
            
            # Save
            sf.write(output_file, audio_arr, self.model.config.sampling_rate)
            logger.info(f"Audio saved to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"TTS Generation error: {e}")
            return None

if __name__ == "__main__":
    tts = SantaliTTS()
    # tts.load_model()
