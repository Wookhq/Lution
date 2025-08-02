#src/Luiton/modules/utils/lang.py
import os
import json
import streamlit as st
if "language" not in st.session_state:
    st.session_state.language = "en"
    
LANG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "files/languages")
lang_files = [f for f in os.listdir(LANG_DIR) if f.endswith(".json")]
LANG_CODES = [os.path.splitext(f)[0] for f in lang_files]
LANG_NAMES = {
    "en": "English",
    "vn": "Tiếng Việt",
    "ger": "Deutsch",
    "lolcat" : "Lolcat 😹 ",
    "premiumenglish": "𝓟𝓻𝓮𝓶𝓲𝓾𝓶  𝓔𝓷𝓰𝓵𝓲𝓼𝓱",
    "tram" : "🚡🚡🚡🚡🚡",
    "sybau" : "sybau.json"

}
def readlang():
    lang_path = os.path.join(LANG_DIR, f"{st.session_state.language}.json")
    with open(lang_path, "r") as f:
        return json.load(f)

LANG = readlang()

def ApplyLanguage(lang):
    st.session_state.language = lang
    print(st.session_state.language)
    global LANG
    LANG = readlang()
