# play history parsed from sober_logs

import json
import re
import urllib.request
from pathlib import Path

SOBER_APP_ID = "org.vinegarhq.Sober"
SOBER_LOGS = Path.home() / ".var/app" / SOBER_APP_ID / "data/sober/sober_logs"
CACHE_DIR = Path.home() / ".local/Lution"
NAMES_CACHE = CACHE_DIR / "game_names.json"

PLACE_RE = re.compile(r'"place_id":"(\d+)","type":"game_loaded"')
HISTORY_LIMIT = 25
def load_name_cache():
    try:
        data = json.loads(NAMES_CACHE.read_text())
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def save_name_cache(cache):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    NAMES_CACHE.write_text(json.dumps(cache, indent=2) + "\n")

def get_history():
    
    entries = {}
    if not SOBER_LOGS.exists():
        return []
    for logfile in SOBER_LOGS.glob("*.log"):
        try:
            text = logfile.read_text(errors="ignore")
        except OSError:
            continue
        matches = PLACE_RE.findall(text)
        if not matches:
            continue
        ts = logfile.stat().st_mtime
        for place_id in matches:
            if place_id == "0":
                continue
            prev = entries.get(place_id)
            if prev is None or ts > prev:
                entries[place_id] = ts
    ranked = sorted(entries.items(), key=lambda kv: kv[1], reverse=True)
    return ranked[:HISTORY_LIMIT]

def _fetch_json(url, timeout=5):
    req = urllib.request.Request(url, headers={"User-Agent": "Lution"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())

def resolve_names(place_ids):
    
    cache = load_name_cache()
    result = {}
    missing = []
    for pid in place_ids:
        if pid in cache:
            result[pid] = cache[pid]
        else:
            missing.append(pid)

    for pid in missing[:6]:
        try:
            uni = _fetch_json(
                f"https://apis.roblox.com/universes/v1/places/{pid}/universe")
            universe_id = uni.get("universeId")
            details = _fetch_json(
                f"https://games.roblox.com/v1/games?universeIds={universe_id}")
            name = details["data"][0]["name"]
        except Exception:
            name = None
        if name:
            cache[pid] = name
            result[pid] = name
        else:
            result[pid] = f"Place {pid}"

    try:
        save_name_cache(cache)
    except Exception:
        pass
    return result

def rel_time(ts):
    import time as _time
    delta = int(_time.time() - ts)
    if delta < 60:
        return "just now"
    if delta < 3600:
        return f"{delta // 60}m ago"
    if delta < 86400:
        return f"{delta // 3600}h ago"
    days = delta // 86400
    if days == 1:
        return "yesterday"
    if days < 7:
        return f"{days}d ago"
    import time as _t
    return _t.strftime("%b %d", _t.localtime(ts))

def launch_place(place_id):
    
    import subprocess
    url = f"roblox://experiences/start?placeId={place_id}"
    subprocess.Popen(["flatpak", "run", SOBER_APP_ID, url],
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL,
                     stdin=subprocess.DEVNULL)
