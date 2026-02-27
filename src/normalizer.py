import string
import re

def normalize_text(text):
    if not text:
        return ""
    # Lowercase conversion
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remove filler phrases
    fillers = ["how can i", "please tell", "can you", "tell me"]
    for filler in fillers:
        text = text.replace(filler, "")
        
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip whitespace
    text = text.strip()
    
    return text
