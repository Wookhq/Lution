# this changes fflags config
# lution now keeps its own config.json and bind mounts it over sober's at launch


from pathlib import Path
import html
import json
import re
import sys
import threading
import time
import urllib.request

import paths
import log
import net

CONFIG_JSON = paths.LUTION_CONFIG
SOBER_CONFIG = paths.SOBER_CONFIG

DEFAULT_CONFIG = {"fflags": {}}
ALLOWLIST_TOPIC = ("https://devforum.roblox.com/t/allowlist-for-local-client-"
                   "configuration-via-fast-flags/3966569.json")
ALLOWLIST_CACHE = paths.STATE_DIR / "fflag_allowlist.json"
ALLOWLIST_BUNDLED = Path(getattr(sys, "_MEIPASS", Path(__file__).parent)) / "fflag_allowlist.json"
ALLOWLIST_REFRESH_AFTER = 24 * 3600
ALLOWLIST_MIN_FLAGS = 10

_FLAG_IN_LISTING = re.compile(r"[A-Za-z][A-Za-z0-9_]{2,}")


def _split_comments(text):
    comment_lines = []
    json_lines = []
    for line in text.splitlines():
        if line.strip().startswith("//"):
            comment_lines.append(line)
        else:
            json_lines.append(line)
    return comment_lines, "\n".join(json_lines)


def _parse(text):
    comment_lines, body = _split_comments(text)
    try:
        data = json.loads(body) if body.strip() else {}
    except json.JSONDecodeError:
        log.error("Could not parse config json :( falling back to defaults")
        return dict(DEFAULT_CONFIG), comment_lines
    if not isinstance(data, dict):
        return dict(DEFAULT_CONFIG), comment_lines
    return data, comment_lines


def load_config():
    base, comments = ({}, [])
    if SOBER_CONFIG.exists():
        base, sober_comments = _parse(SOBER_CONFIG.read_text())
        comments = sober_comments or comments

    data = dict(base)
    fflags = {}
    if CONFIG_JSON.exists():
        lution_data, lution_comments = _parse(CONFIG_JSON.read_text())
        fflags = lution_data.get("fflags") or {}
        if lution_comments:
            comments = lution_comments

    data["fflags"] = fflags
    return data, comments


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
    fflags = data.get("fflags", {})
    return fflags if isinstance(fflags, dict) else {}


def save_fflags(fflags_dict):
    data, comments = load_config()
    data["fflags"] = fflags_dict
    save_config(data, comments)


def _read_allowlist_file(path):
    try:
        data = json.loads(path.read_text())
        allowed = data.get("allowed")
        if isinstance(allowed, list) and allowed:
            return data
    except (OSError, ValueError):
        pass
    return None


def allowlist_file():
    cached = _read_allowlist_file(ALLOWLIST_CACHE)
    if cached:
        return cached
    bundled = _read_allowlist_file(ALLOWLIST_BUNDLED)
    if bundled:
        return bundled
    return {"allowed": [], "updated": "", "source": ALLOWLIST_TOPIC}


def allowlist():
    return set(allowlist_file().get("allowed") or [])


def allowlist_age():
    try:
        data = json.loads(ALLOWLIST_CACHE.read_text())
        return max(0, int(time.time() - float(data.get("_ts", 0))))
    except (OSError, ValueError, TypeError):
        return None


def validate(fflags_dict):
    allowed = allowlist()
    ok, bad = [], []
    for name in fflags_dict:
        (ok if str(name).strip() in allowed else bad).append(name)
    return ok, bad


def clean(fflags_dict):
    ok, bad = validate(fflags_dict)
    kept = {name: fflags_dict[name] for name in ok}
    return kept, bad


def _parse_allowlist_post(payload):
    posts = payload.get("post_stream", {}).get("posts") or []
    if not posts:
        return []
    cooked = posts[0].get("cooked") or ""

    found = []
    for item in re.findall(r"<li>(.*?)</li>", cooked, flags=re.S):
        text = html.unescape(re.sub(r"<[^>]+>", "", item)).strip()
        if _FLAG_IN_LISTING.fullmatch(text) and text not in found:
            found.append(text)
    return found


def refresh_allowlist(timeout=20):
    net.ensure_ca_certs()
    try:
        req = urllib.request.Request(ALLOWLIST_TOPIC,
                                     headers={"User-Agent": "Lution"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read())
        flags = _parse_allowlist_post(payload)
    except Exception as e:
        log.warning(f"Allowlist refresh failed: {e}")
        return False, str(e)

    if len(flags) < ALLOWLIST_MIN_FLAGS:
        msg = f"parsed only {len(flags)} flags, keeping the old list"
        log.warning(f"Allowlist refresh looked wrong: {msg}")
        return False, msg

    ALLOWLIST_CACHE.parent.mkdir(parents=True, exist_ok=True)
    ALLOWLIST_CACHE.write_text(json.dumps({
        "source": ALLOWLIST_TOPIC,
        "updated": time.strftime("%Y-%m-%d"),
        "allowed": flags,
        "_ts": time.time(),
    }, indent=2) + "\n")
    log.info(f"Allowlist refreshed: {len(flags)} flags")
    return True, f"{len(flags)} flags"


def refresh_allowlist_if_stale():
    age = allowlist_age()
    if age is not None and age < ALLOWLIST_REFRESH_AFTER:
        return

    def worker():
        ok, msg = refresh_allowlist()
        if ok:
            log.debug(f"Allowlist auto-updated: {msg}")

    threading.Thread(target=worker, daemon=True).start()
