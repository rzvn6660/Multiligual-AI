import difflib

def get_word_overlap(user_q, db_q):
    # Extract words with length > 3
    user_words = {word for word in user_q.split() if len(word) > 3}
    db_words = {word for word in db_q.split() if len(word) > 3}
    
    # Compute intersection between user question words and DB question words
    overlap = len(user_words.intersection(db_words))
    return overlap

def find_best_match(user_q_norm, db_entries, threshold=0.80):
    best_score = 0.0
    best_match_answer = None
    best_match_question = None
    best_backend = None
    
    for entry in db_entries:
        # Assuming entry format: id, question_eng, answer_sat, backend, similarity_score, created_at
        db_id, db_q, db_a, backend, _, _ = entry
        
        # We need to normalize db_q here or assume it's normalized before passing?
        # The prompt says: "Normalize each stored DB question"
        # Since normalization is fast, we can do it where we call this, or inside.
        # But this function only receives db_q which maybe is raw or normalized. 
        # Actually, let's normalize in the caller.
        
        similarity = difflib.SequenceMatcher(None, user_q_norm, db_q).ratio()
        
        # Word overlap
        overlap = get_word_overlap(user_q_norm, db_q)
        
        # Concept: Cache match is valid ONLY IF similarity >= 0.80 AND keyword overlap > 0
        if similarity >= threshold and overlap > 0:
            if similarity > best_score:
                best_score = similarity
                best_match_answer = db_a
                best_match_question = db_q
                best_backend = backend
                
    return best_score, best_match_answer, best_match_question, best_backend
