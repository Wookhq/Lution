# this only works when you launch sober through lution or the desktop shortcut "Sober with Lution"

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".local/Lution"
ENV_FILE = CONFIG_DIR / "env_vars.json"


def load_vars():
    try:
        data = json.loads(ENV_FILE.read_text())
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def valid_key(key):
    key = key.strip()
    if not key or "=" in key or any(c.isspace() for c in key):
        return False
    return True


def save_vars(vars_dict):
    clean = {}
    for key, value in vars_dict.items():
        key = str(key).strip()
        value = str(value).strip()
        if valid_key(key):
            clean[key] = value
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    ENV_FILE.write_text(json.dumps(clean, indent=2) + "\n")
    return clean


def env_flatpak_args(env_vars=None):
    if env_vars is None:
        env_vars = load_vars()
    return [f"--env={key}={value}" for key, value in env_vars.items()]
