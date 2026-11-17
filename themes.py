# people wanted themes so here
from pathlib import Path
import sys
import json

BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
THEME_FILE = Path.home() / ".local/Lution/theme.json"

DEFAULTS = {
    "accent": "#8D7EDC",
    "bg": "#1e1e1e",
    "bg_sidebar": "#161616",
    "bg_active": "#2a2a2a",
    "fg": "#e0e0e0",
    "fg_dim": "#888888",
    "error": "#e06c75",
    "border": "#161616",
    "input_bg": "#1a1a1a",
    "input_fg": "#e0e0e0",
    "input_border": "#161616",
    "button_bg": "#8D7EDC",
    "button_fg": "#0a0a0a",
    "button_hover": "#7c6fd0",
    "scrollbar": "#3a3a3a",
    "scrollbar_hover": "#5a5a5a",
}

COLOR_KEYS = list(DEFAULTS.keys())


def _valid_color(value):
    if not isinstance(value, str):
        return False
    value = value.strip()
    if len(value) != 7 or not value.startswith("#"):
        return False
    try:
        int(value[1:], 16)
    except ValueError:
        return False
    return True


def load_theme():
    if not THEME_FILE.exists():
        return dict(DEFAULTS)
    try:
        data = json.loads(THEME_FILE.read_text())
        if not isinstance(data, dict):
            return dict(DEFAULTS)
        base = dict(DEFAULTS)
        for key in DEFAULTS:
            if _valid_color(data.get(key)):
                base[key] = data[key].strip()
        return base
    except Exception:
        return dict(DEFAULTS)


def save_theme(colors):
    clean = dict(DEFAULTS)
    for key in DEFAULTS:
        if _valid_color(colors.get(key)):
            clean[key] = colors[key].strip()
    THEME_FILE.parent.mkdir(parents=True, exist_ok=True)
    THEME_FILE.write_text(json.dumps(clean, indent=2) + "\n")