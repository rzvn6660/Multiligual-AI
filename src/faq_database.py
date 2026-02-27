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
                        answer_eng TEXT,
                        answer_sat TEXT,
                        source TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                
                # Verify column existence for legacy DBs
                cursor.execute("PRAGMA table_info(faq)")
                cols = [c[1] for c in cursor.fetchall()]
                if 'answer_eng' not in cols:
                    logger.info("Migrating FAQ DB: Adding language columns...")
                    cursor.execute("ALTER TABLE faq ADD COLUMN answer_eng TEXT")
                    cursor.execute("ALTER TABLE faq ADD COLUMN answer_sat TEXT")
                    # Migrate old 'answer' to 'answer_eng' (assumption) or clear
                    # For safety, we keep 'answer' but ignore it, or we could copy.
                    # Let's assume old 'answer' was English.
                    cursor.execute("UPDATE faq SET answer_eng = answer")
                    conn.commit()
        except Exception as e:
            logger.error(f"FAQ DB Init Error: {e}")

    def normalize(self, text):
        # Basic normalization: lowercase, remove specialized punctuation if needed, strip
        return ' '.join(text.lower().strip().split())

    def get_answer(self, question):
        """
        Tries to find answer in DB. Returns (eng, sat) tuple or None.
        1. Exact match on normalized question.
        2. Fuzzy match using difflib.
        """
        clean_q = self.normalize(question)
        if not clean_q: return None
        
        try:
            with self.get_conn() as conn:
                cursor = conn.cursor()
                
                # 1. Exact Match
                cursor.execute("SELECT answer_eng, answer_sat FROM faq WHERE question_norm = ?", (clean_q,))
                row = cursor.fetchone()
                if row:
                    logger.info(f"FAQ Exact Hit: {clean_q}")
                    return {"eng": row[0], "sat": row[1], "match_type": "EXACT"}
                
                # 2. Fuzzy Match
                cursor.execute("SELECT question_norm, answer_eng, answer_sat FROM faq")
                all_rows = cursor.fetchall()
                if not all_rows: return None
                
                questions = [r[0] for r in all_rows]
                matches = difflib.get_close_matches(clean_q, questions, n=1, cutoff=0.8)
                
                if matches:
                    best_match_q = matches[0]
                    for r in all_rows:
                        if r[0] == best_match_q:
                            logger.info(f"FAQ Fuzzy Hit: '{clean_q}' ~= '{best_match_q}'")
                            return {"eng": r[1], "sat": r[2], "match_type": "FUZZY"}
                            
        except Exception as e:
            logger.error(f"FAQ Read Error: {e}")
            return None
        return None

    def add_entry(self, question, answer_eng, answer_sat, source="LLM"):
        """
        Caches a new Q/A pair with both languages.
        """
        clean_q = self.normalize(question)
        if not answer_eng and not answer_sat: return 
            
        try:
            with self.get_conn() as conn:
                cursor = conn.cursor()
                # Insert or update if exists (if re-caching)
                # For simplicity, we stick to INSERT OR IGNORE, but updating helps fix missing translations.
                
                # Check exist
                cursor.execute("SELECT id FROM faq WHERE question_norm = ?", (clean_q,))
                row = cursor.fetchone()
                
                if row:
                    # Update existing
                     cursor.execute('''
                        UPDATE faq SET answer_eng = ?, answer_sat = ?, source = ? 
                        WHERE question_norm = ?
                    ''', (answer_eng, answer_sat, source, clean_q))
                else:
                    # Insert new
                    cursor.execute('''
                        INSERT INTO faq (question_norm, original_question, answer_eng, answer_sat, source)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (clean_q, question, answer_eng, answer_sat, source))
                conn.commit()
                logger.info(f"FAQ Cached: {clean_q}")
        except Exception as e:
            logger.error(f"FAQ Write Error: {e}")
