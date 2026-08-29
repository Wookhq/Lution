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
    "fg": "#e0e0e0",
}

COLOR_KEYS = ["accent", "bg", "bg_sidebar", "fg"]


def load_theme():
    if not THEME_FILE.exists():
        return dict(DEFAULTS)
    try:
        data = json.loads(THEME_FILE.read_text())
        return {k: data.get(k, DEFAULTS[k]) for k in DEFAULTS}
    except Exception:
        return dict(DEFAULTS)


def save_theme(colors):
    THEME_FILE.parent.mkdir(parents=True, exist_ok=True)
    THEME_FILE.write_text(json.dumps(colors, indent=2) + "\n")
