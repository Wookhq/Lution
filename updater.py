# i hope this works correctly
# omg it did
import urllib.request
import json
import re

import net

VERSION = "0.5.6"
REPO = "wookhq/Lution"
API_URL = f"https://api.github.com/repos/{REPO}/releases/latest"


def parse_version(tag):
    match = re.match(r"^[vV]?(\d+)(?:\.(\d+))?(?:\.(\d+))?", str(tag).strip())
    if not match:
        return None
    return tuple(int(part) if part else 0 for part in match.groups())


def is_newer(remote_tag, current=VERSION):
    remote = parse_version(remote_tag)
    local = parse_version(current)
    if remote is None or local is None:
        return False
    return remote > local


def check_for_update():
    try:
        net.ensure_ca_certs()
        req = urllib.request.Request(API_URL, headers={"User-Agent": "Lution"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        latest = data.get("tag_name", "").lstrip("v")
        url = data.get("html_url", "")
        if not latest:
            return False, None, None
        return is_newer(latest), latest, url
    except Exception:
        return False, None, None
