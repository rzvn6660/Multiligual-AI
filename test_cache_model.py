import os
from src.normalizer import normalize_text
from src.similarity import find_best_match
from src.cache import save_to_cache, check_cache, reset_cache
from src.brain import get_ai_response

def test_cache():
    print("--- Testing Smart Cache & Similarity ---")
    
    # Reset cache to start fresh
    reset_cache()
    
    # 1. Test Normalizer
    print("\n[1] Testing Normalizer...")
    q1 = "How can I grow rice in my field?"
    n1 = normalize_text(q1)
    print(f"Original: {q1}")
    print(f"Normalized: {n1}")
    
    # 2. Add some mock data to cache
    print("\n[2] Seeding Cache...")
    save_to_cache("how to grow rice", "ᱦᱳᱲᱳ ᱪᱟᱥ ᱨᱮᱭᱟᱜ ᱦᱚᱨᱟ (Rice farming steps)", "GEMINI", 0.0)
    save_to_cache("what is the weather today", "ᱛᱮᱦᱮᱧᱟᱜ ᱦᱚᱭ-ᱦᱤᱥᱤᱫ (Today's weather)", "GROQ", 0.0)
    print("Seeded 'how to grow rice' and 'what is the weather today'.")
    
    # 3. Test exact match
    print("\n[3] Testing Exact Match...")
    ans, sim, q, backend = check_cache("How to grow rice?")
    print(f"Result: {ans} | Sim: {sim} | Matched: {q} | Backend: {backend}")
    
    # 4. Test similarity match (high overlap)
    print("\n[4] Testing Similarity Match (High Overlap)...")
    ans, sim, q, backend = check_cache("how can I grow rice")
    print(f"Result: {ans} | Sim: {sim} | Matched: {q} | Backend: {backend}")
    
    # 5. Test word overlap rejection (grow rice vs grow wheat)
    print("\n[5] Testing Overlap Rejection (grow rice vs grow wheat)...")
    ans, sim, q, backend = check_cache("how to grow wheat")
    print(f"Result: {ans} | Sim: {sim} | Matched: {q} | Backend: {backend}")
    if not ans:
        print("Success: Correctly rejected 'wheat' against 'rice' despite high string similarity!")

def test_model():
    print("\n--- Testing Model Selection Logic (brain.py) ---")
    
    # 1. Online - Auto (Should attempt Gemini first)
    print("\n[1] Testing Auto Mode (Will try Gemini -> Groq -> Ollama)...")
    res = get_ai_response("Hello, how are you?", mode="auto")
    print(f"Response: {res}")
    
    # 2. Offline
    print("\n[2] Testing Offline Mode (Will try Ollama)...")
    res = get_ai_response("What is 2+2?", mode="offline")
    print(f"Response: {res}")

if __name__ == "__main__":
    test_cache()
    test_model()
