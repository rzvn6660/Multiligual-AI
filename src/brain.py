from google import genai
import os
import requests
import json
import re
from dotenv import load_dotenv
from src.utils import setup_logger, normalize_text
from groq import Groq

logger = setup_logger("Brain")

# Load environment variables
load_dotenv()

# --- CONSTANTS & CONFIG ---    

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# Updated System Instruction per User Request
# Updated System Instruction per User Request
SYSTEM_INSTRUCTION = (
    "You are a real-time Santali voice assistant designed for tribal users. "
    "Your highest priority is SPEED, ACCURACY, and SIMPLE EXPLANATION. "
    "\n\n"
    "TTS OPTIMIZATION (MANDATORY):\n"
    "- Act as a Text-to-Speech optimization assistant.\n"
    "- Convert all responses into a highly speech-friendly format.\n"
    "- Break long sentences into short, clear sentences (max 10-12 words).\n"
    "- Add natural pauses using commas (,) and full stops (.).\n"
    "- Avoid complex words; use simple and clear language.\n"
    "- Add line breaks between sentences for better speech clarity.\n"
    "- Avoid very long paragraphs — strict rule to split into small chunks.\n"
    "\n\n"
    "VOICE FORMATTING:\n"
    "- Speak like explaining to a beginner.\n"
    "- Keep rhythm slow and natural.\n"
    "- Avoid long lists or compound sentences.\n"
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



def check_safety_intent(text):
    """
    Simple keyword-based intent classification for safety.
    Returns a safe response template if high-risk keywords are found.
    """
    medical_keywords = [
        "diagnosis", "treatment", "medicine", "drug", "dosage", "prescription", 
        "cure", "injection", "pill", "tablet", "surgery", "operation", "clinical", "medication"
    ]
    
    text_lower = text.lower()
    for kw in medical_keywords:
         # precise word matching to avoid false positives (e.g. 'cured' in 'cured meat') implies simple 'in' check is risky
         # but for this specific list, substring match is acceptable for safety
        if kw in text_lower:
             # Return a safe template without calling LLM
             return "This query seems related to medical treatment. I am an AI and cannot provide medical advice. Please consult a doctor or health worker immediately."
    
    return None

def get_ai_response(text, santali_text=None, conversation_history=None, mode="auto"):
    """
    Retrieves response from LLM based on mode and availability.
    Modes: 'auto', 'online', 'offline'
    """
    # PRIORITY 1: SAFETY INTENT CHECK (Guardrail)
    # We check this BEFORE looking at FAQ to ensure we don't return unsafe cached answers.
    clean_text = normalize_text(text)
    safety_msg = check_safety_intent(clean_text)
    if safety_msg:
        logger.info(f"Safety Triggered for: {clean_text}")
        return {"text": safety_msg, "source": "SAFETY_GUARD"}

    # PRIORITIZED CACHE LOGIC IS NOW IN SERVER.PY


    api_key_gemini = os.getenv("GEMINI_API_KEY")
    api_key_groq = os.getenv("GROQ_API_KEY")
    
    # helper to format history
    # helper to format history
    messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
    
    if conversation_history:
        for turn in conversation_history:
            # Map 'model' role to 'assistant' for OpenAI/Groq compatibility
            # Ensure content is string
            role = "assistant" if turn.get("role") == "model" else "user"
            content = str(turn.get("content", ""))
            if content:
                messages.append({"role": role, "content": content})
            
    messages.append({"role": "user", "content": str(text)}) 

    sources_tried = []
    
    # LOGIC:
    # 1. PRIMARY: Groq
    # 2. FALLBACK: Gemini
    # 3. FINAL FALLBACK: Ollama
    
    # 1. PRIMARY (Groq)
    use_groq = mode in ["auto", "online"] and api_key_groq and "gsk_" in api_key_groq
    
    if use_groq:
        try:
            client = Groq(api_key=api_key_groq)
            for model in ["llama-3.1-8b-instant", "llama3-70b-8192", "mixtral-8x7b-32768"]:
                try:
                    chat_completion = client.chat.completions.create(
                        messages=messages,
                        model=model,
                        temperature=0.7,
                        max_tokens=256
                    )
                    if chat_completion.choices:
                        ans = chat_completion.choices[0].message.content.strip()
                        return {"text": ans, "source": "GROQ"}
                except Exception as e:
                    logger.warning(f"Groq {model} failed: {e}")
                    continue
            sources_tried.append("Groq(AllModelsFailed)")
        except Exception as e:
             logger.error(f"Groq Client Init failed: {e}")
             sources_tried.append(f"Groq({e})")

    # 2. FALLBACK (Gemini)
    if mode in ["auto", "online"] and api_key_gemini:
         try:
            client = genai.Client(api_key=api_key_gemini)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{SYSTEM_INSTRUCTION}\n\nUSER: {text}"
            )
            if response.text:
                ans = response.text.strip()
                return {"text": ans, "source": "GEMINI"}
         except Exception as e:
             logger.warning(f"Gemini failed: {e}")
             sources_tried.append(f"Gemini({e})")

    # 3. FINAL FALLBACK (Ollama)
    if mode in ["auto", "offline"]:
        for model_name in ["llama3", "phi3"]:
            try:
                payload = {
                    "model": model_name,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "num_predict": 256
                    }
                }
                res = requests.post(OLLAMA_URL, json=payload, timeout=120)
                if res.status_code == 200:
                    data = res.json()
                    ans = data.get("message", {}).get("content", "").strip()
                    if ans:
                         return {"text": ans, "source": "OLLAMA"}
                else:
                     logger.warning(f"Ollama {model_name} failed with status {res.status_code}")
                     sources_tried.append(f"Ollama({model_name}: Status {res.status_code})")
            except Exception as e:
                logger.error(f"Ollama {model_name} Connection Failed: {e}")
                sources_tried.append(f"Ollama({model_name}: {e})")

    # FAILURE
    logger.error(f"All providers failed. Tried: {sources_tried}")
    
    return {
        "text": FAIL_SAFE_SANTALI,
        "source": "FAIL",
        "error": str(sources_tried),
        "santali_fallback": True
    }
