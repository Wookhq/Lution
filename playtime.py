# playtime from sober's logs

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import history
import log

SOBER_LOGS = history.SOBER_LOGS
CACHE_FILE = Path.home() / ".local/Lution/playtime_cache.json"

MAX_SEGMENT = 12 * 3600
MAX_SESSION = 24 * 3600

_TS_RE = re.compile(r"Roblox: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?)Z")
_GAME_RE = re.compile(r'"place_id":"(\d+)","type":"game_loaded"')


def format_duration(seconds):
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m"
    hours, mins = divmod(seconds // 60, 60)
    if mins:
        return f"{hours}h {mins:02d}m"
    return f"{hours}h"


def _parse_log(path):
    first_ts = last_ts = None
    current = None
    segment_start = None
    segments = {}

    def close_segment(end):
        nonlocal current, segment_start
        if current is not None and segment_start is not None and end is not None:
            delta = end - segment_start
            if 0 <= delta <= MAX_SEGMENT:
                segments[current] = segments.get(current, 0) + delta
        current = None
        segment_start = None

    try:
        lines = path.open(errors="ignore")
    except OSError:
        return 0, {}

    with lines:
        for line in lines:
            stamp = _TS_RE.search(line)
            if stamp:
                try:
                    last_ts = datetime.fromisoformat(
                        stamp.group(1)).replace(tzinfo=timezone.utc).timestamp()
                except ValueError:
                    last_ts = None
                else:
                    if first_ts is None:
                        first_ts = last_ts

            game = _GAME_RE.search(line)
            if game:
                close_segment(last_ts)
                if game.group(1) != "0":
                    current = game.group(1)
                    segment_start = last_ts

    close_segment(last_ts)

    session = 0
    if first_ts is not None and last_ts is not None:
        session = last_ts - first_ts
        if session < 0 or session > MAX_SESSION:
            session = 0

    return session, segments


def _load_cache():
    try:
        data = json.loads(CACHE_FILE.read_text())
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save_cache(cache):
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(json.dumps(cache))
    except OSError as e:
        log.warning(f"Could not save playtime cache: {e}")


def scan():
    if not SOBER_LOGS.exists():
        return totals({})

    cache = _load_cache()
    seen = set()
    changed = False

    for path in sorted(SOBER_LOGS.glob("*.log")):
        if path.is_symlink():
            continue

        try:
            stat = path.stat()
        except OSError:
            continue

        key = path.name
        seen.add(key)
        entry = cache.get(key)
        if (entry and entry.get("size") == stat.st_size
                and entry.get("mtime") == stat.st_mtime):
            continue

        session, segments = _parse_log(path)
        cache[key] = {"size": stat.st_size, "mtime": stat.st_mtime,
                      "session": session, "segments": segments}
        changed = True
        log.debug(f"Playtime: {key} = {format_duration(session)}")

    for key in list(cache):
        if key not in seen:
            del cache[key]
            changed = True

    if changed:
        _save_cache(cache)

    return totals(cache)


def totals(cache=None):
    if cache is None:
        cache = _load_cache()

    places = {}
    session_total = 0.0
    for entry in cache.values():
        session_total += float(entry.get("session") or 0)
        for place_id, seconds in (entry.get("segments") or {}).items():
            places[place_id] = places.get(place_id, 0) + float(seconds)

    return places, session_total, len(cache)
