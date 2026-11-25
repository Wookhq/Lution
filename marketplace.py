# github-hosted marketplace client

import hashlib
import io
import json
import re
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

import atomic
import net
import paths

CACHE_DIR = paths.STATE_DIR

STORE_URL = ("https://raw.githubusercontent.com/wookhq/Lution-Store/"
             "main/store.json")

LOCAL_STORE = CACHE_DIR / "store.json"
STORE_CACHE = CACHE_DIR / "store_cache.json"
INSTALLED_FILE = CACHE_DIR / "marketplace_installed.json"
ICONS_CACHE = CACHE_DIR / "store_icons"

MAX_STORE_BYTES = 4 * 1024 * 1024
MAX_ITEM_BYTES = 256 * 1024 * 1024
MAX_ICON_BYTES = 4 * 1024 * 1024


def _check_url(url):
    parsed = urllib.parse.urlparse(str(url))
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"Refusing non-HTTPS download URL: {url}")
    return str(url)


def _read_limited(resp, limit):
    buf = bytearray()
    while True:
        chunk = resp.read(65536)
        if not chunk:
            break
        buf += chunk
        if len(buf) > limit:
            raise ValueError(f"Download exceeds {limit // (1024 * 1024)} MB limit")
    return bytes(buf)


def _fetch(url, timeout=15, limit=MAX_ITEM_BYTES):
    net.ensure_ca_certs()
    req = urllib.request.Request(_check_url(url),
                                headers={"User-Agent": "Lution"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return _read_limited(resp, limit)

def _parse_items(data):
    parsed = json.loads(data)
    items = parsed.get("items", []) if isinstance(parsed, dict) else parsed
    return items if isinstance(items, list) else []

def fetch_store():
    import log
    try:
        data = _fetch(STORE_URL, limit=MAX_STORE_BYTES)
        items = _parse_items(data)
        if items:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            atomic.write_text(STORE_CACHE, json.dumps(items, indent=2) + "\n")
        return items, False
    except Exception as e:
        log.warning(f"Store fetch failed ({e.__class__.__name__}: {e}), "
                    "using cached copy")
    if LOCAL_STORE.exists():
        try:
            return _parse_items(LOCAL_STORE.read_text()), True
        except Exception as e:
            log.warning(f"Local store.json invalid ({e}), falling back")
    try:
        cached = json.loads(STORE_CACHE.read_text())
        return (cached if isinstance(cached, list) else []), True
    except Exception:
        return [], True

def load_installed():
    try:
        data = json.loads(INSTALLED_FILE.read_text())
        if not isinstance(data, dict):
            return {}
        return {name: info if isinstance(info, dict) else {"sha256": None}
                for name, info in data.items()}
    except Exception:
        return {}

def mark_installed(name, digest=None):
    installed = load_installed()
    installed[name] = {"sha256": digest}
    atomic.write_text(INSTALLED_FILE, json.dumps(installed, indent=2) + "\n")

def is_installed(name):
    return name in load_installed()


def _safe_mod_name(name):
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", str(name).replace(" ", "_"))
    return safe.strip("._")[:80] or "mod"


def _reinstall_mod_for_checksum(item):
    import mods

    data = download(item["url"])
    digest = hashlib.sha256(data).hexdigest()
    expected = item.get("sha256") or item.get("checksum")
    if expected and digest.lower() != str(expected).lower():
        raise ValueError("Download checksum did not match")
    if not zipfile.is_zipfile(io.BytesIO(data)):
        raise ValueError("Downloaded mod is not a ZIP archive")
    mods.ensure_dirs()
    zip_path = mods.MODS_DIR / (_safe_mod_name(item.get("name", "mod")) + ".zip")
    atomic.write_bytes(zip_path, data)
    ok, msg = mods.install_mod(zip_path)
    if not ok:
        raise RuntimeError(msg)
    return digest


def backfill_checksums():
    import log

    installed = load_installed()
    missing = [name for name, info in installed.items()
               if not info.get("sha256")]
    if not missing:
        return []
    items, _from_cache = fetch_store()
    by_name = {item.get("name"): item for item in items
               if isinstance(item, dict) and item.get("name")}
    updated = []
    for name in missing:
        item = by_name.get(name)
        if not item or item.get("type") != "mod" or not item.get("url"):
            mark_installed(name, None)
            log.info(f"Marketplace: kept '{name}' without a checksum "
                     "(no matching mod in store)")
            continue
        try:
            digest = _reinstall_mod_for_checksum(item)
        except Exception as e:
            mark_installed(name, None)
            log.info(f"Marketplace: could not refresh checksum for '{name}': {e}")
            continue
        mark_installed(name, digest)
        updated.append(name)
        log.info(f"Marketplace: refreshed checksum for '{name}'")
    return updated

def download(url, timeout=120):
    return _fetch(url, timeout=timeout)

def download_progress(url, report, timeout=180):
    net.ensure_ca_certs()
    req = urllib.request.Request(_check_url(url),
                                headers={"User-Agent": "Lution"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        length = resp.headers.get("Content-Length")
        total = None
        if length:
            try:
                total = int(length)
            except (TypeError, ValueError):
                total = None
        buf = bytearray()
        got = 0
        while True:
            chunk = resp.read(65536)
            if not chunk:
                break
            buf += chunk
            got += len(chunk)
            if got > MAX_ITEM_BYTES:
                raise ValueError(
                    f"Download exceeds {MAX_ITEM_BYTES // (1024 * 1024)} MB limit")
            if total and total <= MAX_ITEM_BYTES:
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
        if dest.exists() and dest.stat().st_size:
            return dest
        data = _fetch(url, timeout=10, limit=MAX_ICON_BYTES)
        if data[:8] == b"\x89PNG\r\n\x1a\n" or data[:4] == b"GIF8":
            atomic.write_bytes(dest, data)
            return dest
    except Exception:
        pass
    return None
