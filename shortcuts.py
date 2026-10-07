# .desktop entries for bobloc games


import json
import re
import subprocess
import urllib.request
from pathlib import Path

import history
import log
import net
import paths

APPS_DIR = Path.home() / ".local/share/applications"
ICONS_DIR = paths.STATE_DIR / "icons"
PREFIX = "lution-game-"
DESKTOP_SUFFIX = ".desktop"

_BAD_CHARS = re.compile(r"[\r\n\t]+")


def _command(place_id):
    import bootstrapper

    bootstrapper._sync_stable_binary()
    if bootstrapper._is_frozen():
        return f'"{bootstrapper.STABLE_BIN}" --play {place_id}'

    main_py = Path(__file__).parent / "main.py"
    return f'python3 "{main_py}" --play {place_id}'


def _path(place_id):
    return APPS_DIR / f"{PREFIX}{place_id}{DESKTOP_SUFFIX}"


def exists(place_id):
    return _path(str(place_id)).exists()


def _fetch_json(url, timeout=15):
    net.ensure_ca_certs()
    req = urllib.request.Request(url, headers={"User-Agent": "Lution"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def resolve_name(place_id):
    try:
        names = history.resolve_names([str(place_id)])
        return names.get(str(place_id)) or f"Place {place_id}"
    except Exception as e:
        log.debug(f"Could not resolve name for place {place_id}: {e}")
        return f"Place {place_id}"


def fetch_icon(place_id):
    place_id = str(place_id)
    try:
        ICONS_DIR.mkdir(parents=True, exist_ok=True)
        dest = ICONS_DIR / f"{place_id}.png"
        if dest.exists() and dest.stat().st_size > 0:
            return dest

        uni = _fetch_json(
            f"https://apis.roblox.com/universes/v1/places/{place_id}/universe")
        universe_id = uni.get("universeId")
        if not universe_id:
            return None

        thumbs = _fetch_json(
            "https://thumbnails.roblox.com/v1/games/icons"
            f"?universeIds={universe_id}&size=512x512&format=Png"
            "&isCircular=false")
        image_url = (thumbs.get("data") or [{}])[0].get("imageUrl")
        if not image_url:
            return None

        req = urllib.request.Request(image_url, headers={"User-Agent": "Lution"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
        if not data:
            return None

        dest.write_bytes(data)
        return dest
    except Exception as e:
        log.debug(f"Could not fetch icon for place {place_id}: {e}")
        return None


def create(place_id, name=None):
    place_id = str(place_id).strip()
    if not place_id.isdigit():
        raise ValueError("Place ID must be a number")

    game_name = (name or resolve_name(place_id)).strip() or f"Place {place_id}"
    game_name = _BAD_CHARS.sub(" ", game_name)

    icon = fetch_icon(place_id)
    if icon is None:
        fallback = Path.home() / ".local/Lution/sober.svg"
        icon_line = f"Icon={fallback}" if fallback.exists() else ""
    else:
        icon_line = f"Icon={icon}"

    lines = [
        "[Desktop Entry]",
        "Type=Application",
        f"Name={game_name} (Sober)",
        f"Comment=Play {game_name} on Roblox through Lution",
        f"Exec={_command(place_id)}",
        icon_line,
        "Terminal=false",
        "Categories=Game;",
        "StartupWMClass=Lution",
    ]

    APPS_DIR.mkdir(parents=True, exist_ok=True)
    path = _path(place_id)
    path.write_text("\n".join(line for line in lines if line) + "\n")
    path.chmod(0o644)
    _update_database()
    log.info(f"Shortcut created: {game_name} (Sober)")
    return {"place_id": place_id, "name": game_name, "path": str(path)}


def _update_database():
    try:
        subprocess.run(["update-desktop-database", str(APPS_DIR)],
                       capture_output=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        pass


def list_shortcuts():
    if not APPS_DIR.exists():
        return []

    out = []
    for path in APPS_DIR.glob(f"{PREFIX}*{DESKTOP_SUFFIX}"):
        place_id = path.stem[len(PREFIX):]
        if not place_id.isdigit():
            continue

        name = ""
        try:
            for line in path.read_text().splitlines():
                if line.startswith("Name="):
                    name = line[len("Name="):].strip()
                    break
        except OSError:
            continue

        display = name[:-len(" (Sober)")] if name.endswith(" (Sober)") else name
        out.append({"place_id": place_id,
                    "name": display or f"Place {place_id}",
                    "path": str(path)})

    out.sort(key=lambda row: row["name"].lower())
    return out


def remove(place_id):
    path = _path(str(place_id))
    if not path.exists():
        return False
    path.unlink()
    _update_database()
    log.info(f"Shortcut removed: {path.name}")
    return True
