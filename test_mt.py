
from src.mt_provider import IndicTrans2
import logging

logging.basicConfig(level=logging.INFO)
mt = IndicTrans2()

print("Loading MT...")
mt.load_models()

print("Testing Sat -> Eng...")
sat_text = "Johar"
eng = mt.translate(sat_text, src_lang='sat', tgt_lang='eng')
print(f"Sat->Eng: {eng}")

print("Testing Eng -> Sat...")
eng_text = "Hello"
sat = mt.translate(eng_text, src_lang='eng', tgt_lang='sat')
print(f"Eng->Sat: {sat}")
