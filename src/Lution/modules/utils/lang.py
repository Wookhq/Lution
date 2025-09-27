import os
import json
import streamlit as st

if "language" not in st.session_state:
    st.session_state.language = "English"

LANG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "files/languages"
)

# grab folder names
LANG_CODES = [
    d for d in os.listdir(LANG_DIR) if os.path.isdir(os.path.join(LANG_DIR, d))
]

# build display names from folder codes
LANG_NAMES = {code: code for code in LANG_CODES}


def readlang():
    folder = st.session_state.language
    # find the first json file inside that folder
    folder_path = os.path.join(LANG_DIR, folder)
    files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
    if not files:
        raise FileNotFoundError(f"No JSON file found in {folder_path}")
    lang_path = os.path.join(folder_path, files[0])
    with open(lang_path, "r", encoding="utf-8") as f:
        return json.load(f)


LANG = readlang()


def ApplyLanguage(lang):
    st.session_state.language = lang
    global LANG
    LANG = readlang()
