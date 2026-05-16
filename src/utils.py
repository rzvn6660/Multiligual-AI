import logging
import sys

def setup_logger(name):
    """
    Sets up a logger with standard formatting.
    """
    # Ensure stdout handles UTF-8 (Vital for Windows)
    if hasattr(sys.stdout, 'reconfigure') and sys.stdout.encoding.lower() != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
            
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add handler to logger
    if not logger.handlers:
        logger.addHandler(handler)
        
        # Also log to file with UTF-8 encoding
        file_handler = logging.FileHandler("server_debug.log", encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

def normalize_text(text):
    import string
    import re
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

def get_word_overlap(user_q, db_q):
    # Extract words with length > 3
    user_words = {word for word in user_q.split() if len(word) > 3}
    db_words = {word for word in db_q.split() if len(word) > 3}
    
    # Compute intersection between user question words and DB question words
    overlap = len(user_words.intersection(db_words))
    return overlap

def find_best_match(user_q_norm, db_entries, threshold=0.80):
    import difflib
    best_score = 0.0
    best_match_answer = None
    best_match_question = None
    best_backend = None
    
    for entry in db_entries:
        db_id, db_q, db_a, backend, _, _ = entry
        
        similarity = difflib.SequenceMatcher(None, user_q_norm, db_q).ratio()
        
        overlap = get_word_overlap(user_q_norm, db_q)
        
        if similarity >= threshold and overlap > 0:
            if similarity > best_score:
                best_score = similarity
                best_match_answer = db_a
                best_match_question = db_q
                best_backend = backend
                
    return best_score, best_match_answer, best_match_question, best_backend
