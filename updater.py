# i hope this works correctly
import urllib.request
import json

VERSION = "0.4.3"
REPO = "wookhq/Lution"
API_URL = f"https://api.github.com/repos/{REPO}/releases/latest"


def check_for_update():
    try:
        req = urllib.request.Request(API_URL, headers={"User-Agent": "Lution"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        latest = data.get("tag_name", "").lstrip("v")
        url = data.get("html_url", "")
        if not latest:
            return False, None, None
        current = tuple(int(x) for x in VERSION.split("."))
        remote = tuple(int(x) for x in latest.split("."))
        return remote > current, latest, url
    except Exception:
        return False, None, None
