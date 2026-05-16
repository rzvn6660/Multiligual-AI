import sqlite3
import os
import datetime
from src.utils import setup_logger, normalize_text, find_best_match

logger = setup_logger("SmartCache")

DB_PATH = "triem_cache.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS faq_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_eng TEXT UNIQUE,
            answer_sat TEXT,
            backend TEXT,
            similarity_score REAL,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def reset_cache():
    """Manual trigger to drop and recreate cache db"""
    logger.info("Manual cache reset triggered.")
    if os.path.exists(DB_PATH):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('DROP TABLE IF EXISTS faq_cache')
        c.execute('''
            CREATE TABLE faq_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_eng TEXT UNIQUE,
                answer_sat TEXT,
                backend TEXT,
                similarity_score REAL,
                created_at TEXT
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("Cache reset successful. Table 'faq_cache' recreated.")
    else:
        logger.info("Cache DB does not exist, initializing fresh.")
        init_db()

def fetch_latest_entries(limit=500):
    init_db()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, question_eng, answer_sat, backend, similarity_score, created_at FROM faq_cache ORDER BY id DESC LIMIT ?', (limit,))
    entries = c.fetchall()
    conn.close()
    return entries

def check_cache(english_question):
    """
    Checks cache for a match based on the English question.
    Normalizes user question and DB questions.
    Returns best_match_answer, similarity_score, best_match_question, backend
    """
    user_q_norm = normalize_text(english_question)
    
    # Fetch 500 latest entries
    entries = fetch_latest_entries(500)
    
    # Normalize DB questions before matching
    normalized_entries = []
    for entry in entries:
        db_id, db_q, db_a, backend, sim, created_at = entry
        db_q_norm = normalize_text(db_q)
        normalized_entries.append((db_id, db_q_norm, db_a, backend, sim, created_at))
        
    best_score, best_match_answer, best_match_question, best_backend = find_best_match(
        user_q_norm, normalized_entries, threshold=0.80
    )
    
    return best_match_answer, best_score, best_match_question, best_backend

def save_to_cache(question_eng, answer_sat, backend, similarity_score=0.0):
    init_db()
    timestamp = datetime.datetime.now().isoformat()
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT OR IGNORE INTO faq_cache (question_eng, answer_sat, backend, similarity_score, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (question_eng, answer_sat, backend, similarity_score, timestamp))
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to save to cache: {e}")
    finally:
        conn.close()
