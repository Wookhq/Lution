# github-hosted marketplace client

import json
import urllib.request
from pathlib import Path

CACHE_DIR = Path.home() / ".local/Lution"

STORE_URL = ("https://raw.githubusercontent.com/wookhq/Lution-Store/"
             "main/store.json")

LOCAL_STORE = CACHE_DIR / "store.json"
STORE_CACHE = CACHE_DIR / "store_cache.json"
INSTALLED_FILE = CACHE_DIR / "marketplace_installed.json"
ICONS_CACHE = CACHE_DIR / "store_icons"

def _fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "Lution"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()

def _parse_items(data):
    parsed = json.loads(data)
    items = parsed.get("items", []) if isinstance(parsed, dict) else parsed
    return items if isinstance(items, list) else []

def fetch_store():
    
    if LOCAL_STORE.exists():
        try:
            return _parse_items(LOCAL_STORE.read_text())
        except Exception as e:
            import log
            log.warning(f"Local store.json invalid ({e}), falling back")
    try:
        data = _fetch(STORE_URL)
        items = _parse_items(data)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        STORE_CACHE.write_text(json.dumps(items, indent=2) + "\n")
        return items
    except Exception:
        pass
    try:
        cached = json.loads(STORE_CACHE.read_text())
        return cached if isinstance(cached, list) else []
    except Exception:
        return []

def load_installed():
    try:
        data = json.loads(INSTALLED_FILE.read_text())
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def mark_installed(name):
    installed = load_installed()
    installed[name] = True
    INSTALLED_FILE.parent.mkdir(parents=True, exist_ok=True)
    INSTALLED_FILE.write_text(json.dumps(installed, indent=2) + "\n")

def is_installed(name):
    return name in load_installed()

def download(url, timeout=120):
    return _fetch(url, timeout=timeout)

def download_progress(url, report, timeout=180):
    
    req = urllib.request.Request(url, headers={"User-Agent": "Lution"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        length = resp.headers.get("Content-Length")
        total = int(length) if length else None
        buf = bytearray()
        got = 0
        while True:
            chunk = resp.read(65536)
            if not chunk:
                break
            buf += chunk
            got += len(chunk)
            if total:
                report(got / total, f"{got // 1024} KB / {total // 1024} KB")
            else:
                report(None, f"{got // 1024} KB")
        return bytes(buf)

def fetch_icon(name, url):
    
    import re as _re
    ext_match = _re.search(r"\.(png|gif)$", url.lower())
    ext = ext_match.group(1) if ext_match else "png"
    safe = _re.sub(r"[^A-Za-z0-9_-]", "_", name)[:40] or "item"
    try:
        ICONS_CACHE.mkdir(parents=True, exist_ok=True)
        dest = ICONS_CACHE / f"{safe}.{ext}"
        if dest.exists():
            return dest
        data = _fetch(url, timeout=10)
        if data[:8] == b"\x89PNG\r\n\x1a\n" or data[:4] == b"GIF8":
            dest.write_bytes(data)
            return dest
    except Exception:
        pass
    return None
