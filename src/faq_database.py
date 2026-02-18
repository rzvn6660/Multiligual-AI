import sqlite3
import difflib
import os
from src.utils import setup_logger

logger = setup_logger("FAQ_DB")

DB_PATH = "faq_cache.db"

class FAQManager:
    def __init__(self):
        self.init_db()

    def get_conn(self):
        return sqlite3.connect(DB_PATH, check_same_thread=False)

    def init_db(self):
        try:
            with self.get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS faq (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        question_norm TEXT UNIQUE,
                        original_question TEXT,
                        answer TEXT,
                        source TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
        except Exception as e:
            logger.error(f"FAQ DB Init Error: {e}")

    def normalize(self, text):
        # Basic normalization: lowercase, remove specialized punctuation if needed, strip
        return ' '.join(text.lower().strip().split())

    def get_answer(self, question):
        """
        Tries to find an answer in the DB.
        1. Exact match on normalized question.
        2. Fuzzy match using difflib.
        """
        clean_q = self.normalize(question)
        if not clean_q:
            return None
            
        try:
            with self.get_conn() as conn:
                cursor = conn.cursor()
                
                # 1. Exact Match
                cursor.execute("SELECT answer FROM faq WHERE question_norm = ?", (clean_q,))
                row = cursor.fetchone()
                if row:
                    logger.info(f"FAQ Exact Hit: {clean_q}")
                    return row[0]
                
                # 2. Fuzzy Match (Fetch all questions)
                # Note: valid for < 10,000 items. If larger, move to FTS.
                cursor.execute("SELECT question_norm, answer FROM faq")
                all_rows = cursor.fetchall()
                
                if not all_rows:
                    return None
                
                # List of questions
                questions = [r[0] for r in all_rows]
                
                # Get close matches (cutoff 0.7 means 70% similarity)
                matches = difflib.get_close_matches(clean_q, questions, n=1, cutoff=0.7)
                
                if matches:
                    best_match_q = matches[0]
                    # Retrieve answer for the matched question
                    for q, ans in all_rows:
                        if q == best_match_q:
                            logger.info(f"FAQ Fuzzy Hit: '{clean_q}' ~= '{best_match_q}'")
                            return ans
                            
        except Exception as e:
            logger.error(f"FAQ Read Error: {e}")
            return None
        
        return None

    def add_entry(self, question, answer, source="LLM"):
        """
        Caches a new Q/A pair.
        """
        clean_q = self.normalize(question)
        if not answer or len(answer) < 5: 
            return 
            
        try:
            with self.get_conn() as conn:
                cursor = conn.cursor()
                # Insert if unique
                cursor.execute('''
                    INSERT OR IGNORE INTO faq (question_norm, original_question, answer, source)
                    VALUES (?, ?, ?, ?)
                ''', (clean_q, question, answer, source))
                conn.commit()
                # If it was ignored, maybe update it? 
                # For now, we respect the FIRST answer as canonical unless manual clearing.
                logger.info(f"FAQ Cached: {clean_q}")
        except Exception as e:
            logger.error(f"FAQ Write Error: {e}")
