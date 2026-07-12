# this changes fflags config

from pathlib import Path
import json

SOBER_APP_ID = "org.vinegarhq.Sober"
CONFIG_JSON = Path.home() / ".var/app" / SOBER_APP_ID / "config/sober/config.json"


def load_config():
    if not CONFIG_JSON.exists():
        return {"fflags": {}}, []

    comment_lines = []
    json_lines = []
    for line in CONFIG_JSON.read_text().splitlines():
        if line.strip().startswith("//"):
            comment_lines.append(line)
        else:
            json_lines.append(line)

    data = json.loads("\n".join(json_lines)) if json_lines else {}
    data.setdefault("fflags", {})
    return data, comment_lines


def save_config(data, comment_lines):
    CONFIG_JSON.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(data, indent=4)
    header = ("\n".join(comment_lines) + "\n") if comment_lines else ""
    CONFIG_JSON.write_text(header + body + "\n")


def parse_value(raw):
    text = raw.strip()
    if text.lower() == "true":
        return True
    if text.lower() == "false":
        return False
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        pass
    return text


def get_fflags():
    data, _ = load_config()
    return data.get("fflags", {})


def save_fflags(fflags_dict):
    data, comments = load_config()
    data["fflags"] = fflags_dict
    save_config(data, comments)
