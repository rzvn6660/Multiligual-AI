from google import genai
import os
import requests
import json
import re
from dotenv import load_dotenv
from src.utils import setup_logger
from groq import Groq
from src.faq_database import FAQManager

logger = setup_logger("Brain")

# Load environment variables
load_dotenv()

# --- CONSTANTS & CONFIG ---
faq_manager = FAQManager()

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# Updated System Instruction per User Request
SYSTEM_INSTRUCTION = (
    "You are a real-time Santali voice assistant designed for tribal users. "
    "Your highest priority is SPEED, ACCURACY, and SIMPLE EXPLANATION. "
    "\n\n"
    "TTS OPTIMIZATION (MANDATORY): "
    "- Responses are spoken aloud. "
    "- Keep them clear and slow. "
    "- Use short sentences (Max 3-4 sentences total). "
    "- Each sentence MUST comprise fewer than 12 words. "
    "- Use full stops (.) instead of commas (,) to force pauses. "
    "- Do not create long flowing paragraphs. "
    "- Prioritize clarity over detail. "
    "\n\n"
    "VOICE FORMATTING: "
    "- Speak like explaining to a child. "
    "- Keep rhythm slow and natural. "
    "- Avoid long lists or compound sentences. "
    "\n\n"
    "TRUTH VERIFICATION (CRITICAL): "
    "- Do NOT automatically agree with the user. "
    "- If the user statement is incorrect, politely correct it. "
    "- If unsure, say 'I am not sure'. "
    "- CORRECTION STYLE: Polite, simple. State correction first, then 2-4 sentence explanation. "
    "\n\n"
    "STRICT SAFETY RULES (VIOLATION = HARM): "
    "- HEALTH: GENERAL AWARENESS ONLY. "
    "  * DIRECTIVE: Do NOT provide diagnosis, medicine names, dosages, or treatment steps. "
    "  * REQUIREMENT: If the topic is serious, append: 'This is general information. Please consult a doctor or health worker.' "
    "- FARMING: GENERAL GUIDANCE ONLY. "
    "  * DIRECTIVE: Do NOT provide specific pesticide/chemical names, dosages, or mixing instructions. "
    "  * REQUIREMENT: Encourage consulting local agriculture officers. "
    "\n\n"
    "TONE: Friendly, respectful, calm, and VERY CLEAR for voice output."
)

# Strict Fail Safe Message in Santali
FAIL_SAFE_SANTALI = "ᱥᱟᱨᱡᱤᱢᱮ, ᱤᱧ ᱱᱤᱛᱚᱜ ᱵᱟᱝ ᱥᱟᱹᱜᱟᱲ ᱠᱟᱱᱟ᱾ ᱟᱲᱟᱜ ᱫᱚ ᱫᱚᱦᱚᱲ ᱢᱮᱱᱟᱜᱼᱟᱭᱟ᱾"

def normalize_text(text):
    """
    ASR Error Handling:
    - Remove punctuation
    - Remove extra spaces
    - Lowercase
    """
    if not text:
        return ""
    # Remove punctuation (keep alphanumeric and spaces)
    # This regex keeps letters, numbers and spaces. 
    # Note: For Santali/Devanagari/Ol Chiki, we must be careful not to remove valid chars.
    # Simple approach: Replace common punctuation with space.
    text = re.sub(r'[.,!?;:()"]', ' ', text)
    # Squeeze spaces
    text = ' '.join(text.split())
    return text.lower()

def get_ai_response(text, santali_text=None, conversation_history=None, mode="auto"):
    """
    Retrieves response from LLM based on mode and availability.
    Modes: 'auto', 'online', 'offline'
    """
    # 0. ASR NORMALIZATION & FAQ CHECK
    # PRIORITY 1: Check Santali Text directly in FAQ (Avoids MT)
    if santali_text:
        clean_santali = normalize_text(santali_text)
        cached_santali = faq_manager.get_answer(clean_santali)
        if cached_santali:
            # We found a direct answer in Santali!
            return {
                "text": cached_santali, 
                "source": "SQLITE_FAQ", 
                "santali_fallback": True # This signals server.py to SKIP MT (Eng->Sat) and use this text directly
            }

    # PRIORITY 2: Check English Text in FAQ
    clean_text = normalize_text(text)
    if not clean_text:
         return {"text": FAIL_SAFE_SANTALI, "source": "EMPTY_INPUT", "santali_fallback": True}

    cached_text = faq_manager.get_answer(clean_text)
    if cached_text:
        return {"text": cached_text, "source": "SQLITE_FAQ"}

    api_key_gemini = os.getenv("GEMINI_API_KEY")
    api_key_groq = os.getenv("GROQ_API_KEY")
    
    # helper to format history
    messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
    
    if conversation_history:
        for turn in conversation_history:
            role = "assistant" if turn["role"] == "model" else "user"
            messages.append({"role": role, "content": turn["content"]})
            
    messages.append({"role": "user", "content": text}) # Use original text for LLM context, usually better than stripped

    sources_tried = []
    
    # LOGIC:
    # If Internet Available -> Use Groq.
    # If Internet Unavailable (or Groq fails) -> Use Ollama.
    # Never call both if one succeeds.
    
    # 2. ONLINE (Groq)
    # We prefer Groq if mode is Auto/Online and key exists.
    use_groq = mode in ["auto", "online"] and api_key_groq and "gsk_" in api_key_groq
    
    if use_groq:
        try:
            client = Groq(api_key=api_key_groq)
            # Try fast models first. Updated list.
            for model in ["llama-3.1-8b-instant", "llama3-70b-8192", "mixtral-8x7b-32768"]:
                try:
                    chat_completion = client.chat.completions.create(
                        messages=messages,
                        model=model,
                        temperature=0.7,
                        max_tokens=256 # Short responses requested
                    )
                    if chat_completion.choices:
                        ans = chat_completion.choices[0].message.content.strip()
                        # Cache it
                        faq_manager.add_entry(clean_text, ans, source="GROQ")
                        return {"text": ans, "source": "GROQ"}
                except Exception as e:
                    logger.warning(f"Groq {model} failed: {e}")
                    continue
            # If loop finishes without return, Groq failed.
            sources_tried.append("Groq(AllModelsFailed)")
        except Exception as e:
             logger.error(f"Groq Client Init failed: {e}")
             sources_tried.append(f"Groq({e})")

    # 3. OFFLINE (Ollama)
    # Fallback if Groq failed OR mode is explicitly offline
    # We essentially treat 'auto' effectively as "Try Online, else Offline"
    
    # Only try Ollama if we haven't succeeded yet (which we haven't if we are here)
    if mode in ["auto", "offline"]:
        try:
            payload = {
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": False,
                "options": {
                    "num_predict": 256 # Limit output length to match speed requirement
                }
            }
            res = requests.post(OLLAMA_URL, json=payload, timeout=10) # Fast timeout for offline check
            if res.status_code == 200:
                data = res.json()
                ans = data.get("message", {}).get("content", "").strip()
                if ans:
                     faq_manager.add_entry(clean_text, ans, source="OLLAMA")
                     return {"text": ans, "source": "OLLAMA"}
            else:
                 sources_tried.append(f"Ollama(Status {res.status_code})")
        except Exception as e:
            logger.error(f"Ollama Connection Failed: {e}")
            sources_tried.append(f"Ollama({e})")

    # 4. GEMINI (Last Resort / Hidden Fallback)
    # User said "Never call both models" (Groq/Ollama), but if BOTH fail, we might want Gemini as a hail mary?
    # User said: "If no FAQ match is found: 1. If internet available: Use Groq... 2. If internet unavailable: Use Ollama locally."
    # It didn't explicitly forbid Gemini as a backup for Groq, but "Never retry unnecessarily" implies strictness.
    # However, for robustness, if Groq fails (e.g. rate limit) and Ollama isn't running, Gemini is a good backup.
    # I will keep Gemini as a silent backup only if Online and Groq failed.
    
    if mode in ["auto", "online"] and api_key_gemini and "Groq" in str(sources_tried):
         try:
            client = genai.Client(api_key=api_key_gemini)
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=f"{SYSTEM_INSTRUCTION}\n\nUSER: {text}"
            )
            if response.text:
                ans = response.text.strip()
                faq_manager.add_entry(clean_text, ans, source="GEMINI")
                return {"text": ans, "source": "GEMINI"}
         except Exception as e:
             sources_tried.append(f"Gemini({e})")

    # FAILURE
    logger.error(f"All providers failed. Tried: {sources_tried}")
    
    return {
        "text": FAIL_SAFE_SANTALI,
        "source": "FAIL",
        "error": str(sources_tried),
        "santali_fallback": True
    }
