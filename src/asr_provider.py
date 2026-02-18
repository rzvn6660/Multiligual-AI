import torch
import torchaudio
from transformers import AutoModel
from src.utils import setup_logger
from src.config_hf import Config

logger = setup_logger("ASR_Provider")

class SantaliASR:
    def __init__(self):
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.target_sample_rate = 16000
        
    def load_model(self):
        try:
            logger.info(f"Loading ASR Model: {Config.ASR_MODEL_NAME}...")
            # Using trust_remote_code=True as required by the model
            self.model = AutoModel.from_pretrained(Config.ASR_MODEL_NAME, trust_remote_code=True)
            
            if torch.cuda.is_available():
                self.model = self.model.cuda()
            
            self.model.eval()
            
            logger.info("ASR Model loaded successfully.")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load ASR: {e}")
            return False

    def transcribe(self, audio_file_path, language="sat", decoding="ctc"):
        """
        Transcribe the audio file.
        :param audio_file_path: Path to the audio file
        :param language: Language code (default 'sat' for Santali). 
                         Use 'hi', 'bn', etc. for others.
        :param decoding: 'ctc' or 'rnnt' (default 'ctc')
        """
        if not self.model:
            logger.error("ASR Model not loaded.")
            return ""
            
        try:
            logger.info(f"Transcribing {audio_file_path} (Lang: {language}, Decoding: {decoding})...")
            
            # Load audio using torchaudio
            wav, sr = torchaudio.load(audio_file_path)
            
            # Convert to mono if necessary
            if wav.shape[0] > 1:
                wav = torch.mean(wav, dim=0, keepdim=True)
                
            # Resample if necessary
            if sr != self.target_sample_rate:
                resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=self.target_sample_rate)
                wav = resampler(wav)

            # Move to device
            if torch.cuda.is_available():
                wav = wav.to(self.device)

            # Perform Inference
            with torch.no_grad():
                transcription = self.model(wav, language, decoding)
                
            logger.info(f"ASR Output: {transcription}")
            return str(transcription)

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""

if __name__ == "__main__":
    asr = SantaliASR()
    if asr.load_model():
        pass
