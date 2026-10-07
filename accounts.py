# who you are signed in as and what your friends are doing

import json
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import log
import net
import paths

SOBER_DATA = Path.home() / ".var/app/org.vinegarhq.Sober/data/sober"
COOKIES_FILE = SOBER_DATA / "cookies"
APP_STORAGE = SOBER_DATA / "appData/LocalStorage/appStorage.json"

CACHE_DIR = paths.STATE_DIR / "social"
PROFILE_CACHE = CACHE_DIR / "profile.json"
AVATAR_DIR = CACHE_DIR / "avatars"

MEMORY_TTL = 60
DISK_TTL = 6 * 3600
AVATAR_TTL = 24 * 3600

OFFLINE, ONLINE, IN_GAME, IN_STUDIO = 0, 1, 2, 3

_memory = {"ts": 0, "data": None}


class AccountError(Exception):
    pass


def cookie_header():
    try:
        text = COOKIES_FILE.read_text().strip()
    except OSError:
        return None
    if not text or ".ROBLOSECURITY" not in text:
        return None
    return text


def _request(url, data=None, cookie=False, timeout=15):
    headers = {"User-Agent": "Lution", "Accept": "application/json",
               "Content-Type": "application/json"}
    if cookie:
        jar = cookie_header()
        if not jar:
            raise AccountError("Sober has no saved login yet - open Sober and "
                               "sign in once, then retry.")
        headers["Cookie"] = jar

    net.ensure_ca_certs()
    req = urllib.request.Request(
        url, data=json.dumps(data).encode() if data is not None else None,
        headers=headers, method="POST" if data is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code in (401, 403) and cookie:
            raise AccountError(
                "Sober's login has expired - open Sober and sign in again.") from e
        raise AccountError(f"Roblox replied with HTTP {e.code}") from e
    except urllib.error.URLError as e:
        raise AccountError(f"Network error: {e.reason}") from e


def current_user():
    me = _request("https://users.roblox.com/v1/users/authenticated", cookie=True)
    return {"id": me.get("id"), "name": me.get("name", ""),
            "display_name": me.get("displayName", ""),
            "created": me.get("created", "")}


def switcher_accounts():
    try:
        storage = json.loads(APP_STORAGE.read_text())
    except (OSError, ValueError) as e:
        log.debug(f"Could not read appStorage: {e}")
        return []

    raw = storage.get("PreviousAccountsList") or "{}"
    try:
        entries = json.loads(raw) if isinstance(raw, str) else raw
    except ValueError:
        entries = {}
    if not isinstance(entries, dict):
        return []

    rows = []
    for user_id, info in entries.items():
        if not isinstance(info, dict):
            continue
        rows.append({
            "id": str(user_id),
            "name": info.get("username") or info.get("userIdentifier") or "",
            "display_name": info.get("displayName") or "",
            "signed_out": bool(info.get("signOutTimestamp")),
            "last_signed_in": int(info.get("signInTimestamp") or 0),
        })
    rows.sort(key=lambda r: (r["signed_out"], -r["last_signed_in"]))
    return rows


def friend_list(user_id):
    raw = _request(
        f"https://friends.roblox.com/v1/users/{user_id}/friends?limit=200",
        cookie=True)
    ids = [row.get("id") for row in raw.get("data", []) if row.get("id")]

    details = {}
    for start in range(0, len(ids), 100):
        chunk = ids[start:start + 100]
        resp = _request("https://users.roblox.com/v1/users", {"userIds": chunk})
        for user in resp.get("data", []):
            details[user["id"]] = user

    friends = []
    for uid in ids:
        user = details.get(uid, {})
        friends.append({
            "id": uid,
            "name": user.get("name", ""),
            "display_name": user.get("displayName") or f"User {uid}",
            "created": user.get("created", ""),
        })
    return friends


def presence_map(user_ids):
    ids = [int(u) for u in user_ids if u]
    out = {}
    for start in range(0, len(ids), 100):
        chunk = ids[start:start + 100]
        resp = _request("https://presence.roblox.com/v1/presence/users",
                        {"userIds": chunk}, cookie=True)
        for row in resp.get("userPresences", []):
            out[row.get("userId")] = {
                "type": row.get("userPresenceType", OFFLINE),
                "location": row.get("lastLocation") or "",
                "place_id": row.get("placeId"),
                "root_place_id": row.get("rootPlaceId"),
                "universe_id": row.get("universeId"),
                "game_id": row.get("gameId"),
            }
    return out


def status_text(presence):
    if not presence:
        return "Offline", OFFLINE
    kind = presence.get("type", OFFLINE)
    location = presence.get("location") or ""
    if kind == IN_GAME:
        return f"Playing {location}" if location else "Playing an experience", kind
    if kind == IN_STUDIO:
        return "In Studio", kind
    if kind == ONLINE:
        return "Online", kind
    return "Offline", kind


def join_url(presence):
    if not presence:
        return None
    place_id = presence.get("place_id") or presence.get("root_place_id")
    if not place_id:
        return None
    url = f"roblox://experiences/start?placeId={place_id}"
    if presence.get("game_id"):
        url += f"&gameInstanceId={presence['game_id']}"
    return url


def _download(url, dest, timeout=20):
    net.ensure_ca_certs()
    req = urllib.request.Request(url, headers={"User-Agent": "Lution"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
    if data:
        dest.write_bytes(data)


def download_avatars(user_ids):
    AVATAR_DIR.mkdir(parents=True, exist_ok=True)
    now = time.time()
    ids = list(dict.fromkeys(int(u) for u in user_ids if u))

    urls = {}
    for start in range(0, len(ids), 100):
        chunk = ids[start:start + 100]
        query = ",".join(str(u) for u in chunk)
        resp = _request("https://thumbnails.roblox.com/v1/users/avatar-headshot"
                        f"?userIds={query}&size=150x150&format=Png"
                        "&isCircular=false")
        for row in resp.get("data", []):
            if row.get("state") == "Completed" and row.get("imageUrl"):
                urls[row["targetId"]] = row["imageUrl"]

    def ensure(uid):
        dest = AVATAR_DIR / f"{uid}.png"
        try:
            fresh = dest.exists() and now - dest.stat().st_mtime < AVATAR_TTL
            if not fresh and uid in urls:
                _download(urls[uid], dest)
        except Exception as e:
            log.debug(f"Avatar {uid} not fetched: {e}")
        return uid, (str(dest) if dest.exists() else None)
    with ThreadPoolExecutor(max_workers=8) as pool:
        return {str(uid): path for uid, path in pool.map(ensure, ids)}


def fetch_all(refresh=False, timeout=20):
    now = time.time()
    if not refresh and _memory["data"] and now - _memory["ts"] < MEMORY_TTL:
        return _memory["data"]

    try:
        user = current_user()
        accounts = switcher_accounts()
        for account in accounts:
            account["active"] = account["id"] == str(user["id"])
            if account["active"] and not account["display_name"]:
                account["display_name"] = user["display_name"]
        friends = friend_list(user["id"])
        presence = presence_map([f["id"] for f in friends] + [user["id"]])
        avatars = download_avatars(
            [f["id"] for f in friends] + [user["id"]]
            + [a["id"] for a in accounts if a["id"].isdigit()])
        data = {"user": user, "accounts": accounts, "friends": friends,
                "presence": presence, "avatars": avatars, "ts": now}
    except AccountError as e:
        cached = _disk_cache()
        if cached:
            log.warning(f"Account refresh failed ({e}), using cached data")
            return cached
        raise

    _memory.update(ts=now, data=data)
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        PROFILE_CACHE.write_text(json.dumps(data))
    except OSError:
        pass
    log.debug(f"Account: {user['name']}, {len(friends)} friends, "
              f"{sum(1 for p in presence.values() if p['type'] == IN_GAME)} in game")
    return data


def _disk_cache():
    if not _memory["data"]:
        try:
            data = json.loads(PROFILE_CACHE.read_text())
            if isinstance(data, dict) and time.time() - data.get("ts", 0) < DISK_TTL:
                _memory.update(ts=data["ts"], data=data)
                return data
        except (OSError, ValueError):
            pass
    return _memory["data"]
