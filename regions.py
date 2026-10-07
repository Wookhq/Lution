# server region lookup n matchmaking
# W rovalra
import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

import log
import net
import paths

ROVALRA = "https://apis.rovalra.com"
ROBLOX_GAMES = "https://games.roblox.com/v1"
IPINFO_URL = "https://ipinfo.io/json"

STATE = paths.STATE_DIR
DATACENTERS_CACHE = STATE / "datacenters.json"
LOCATION_CACHE = STATE / "location.json"

DATACENTERS_TTL = 7 * 24 * 3600
LOCATION_TTL = 6 * 3600

PAGE_LIMIT = 100
MAX_PAGES = 4
MAX_ROWS = 120

ANY_REGION = "Any region"
AUTO_REGION = "Auto (nearest)"


class RegionError(Exception):
    pass


def _get(url, timeout=20):
    net.ensure_ca_certs()
    req = urllib.request.Request(url, headers={"User-Agent": "Lution"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RegionError(
                "Roblox is rate limiting requests right now - wait a moment "
                "and try again") from e
        raise RegionError(f"Request failed with HTTP {e.code}") from e
    except urllib.error.URLError as e:
        raise RegionError(f"Network error: {e.reason}") from e


def _cache_read(path, ttl):
    try:
        data = json.loads(path.read_text())
        if time.time() - float(data.get("_ts", 0)) < ttl:
            return data.get("items")
    except (OSError, ValueError, TypeError):
        pass
    return None


def _cache_write(path, items):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"_ts": time.time(), "items": items}))
    except OSError:
        pass


def _label(city, country_code):
    city = (city or "").strip()
    country_code = (country_code or "").strip()
    if not city or not country_code:
        return None
    return f"{city}, {country_code}"


def datacenters(refresh=False):
    if not refresh:
        cached = _cache_read(DATACENTERS_CACHE, DATACENTERS_TTL)
        if cached:
            return cached

    raw = _get(f"{ROVALRA}/v1/datacenters/list", timeout=25)
    if not isinstance(raw, list) or not raw:
        raise RegionError("RoValra returned no datacenters")

    rows = []
    seen = set()
    for entry in raw:
        loc = (entry or {}).get("location") or {}
        city = (loc.get("city") or "").strip()
        country = (loc.get("country") or "").strip()
        if not city or not country:
            continue
        key = f"{city}, {country}"
        if key in seen:
            continue
        seen.add(key)

        latlong = loc.get("latLong") or []
        try:
            lat, lon = float(latlong[0]), float(latlong[1])
        except (IndexError, TypeError, ValueError):
            lat = lon = None

        rows.append({"label": key, "city": city, "country": country,
                     "lat": lat, "lon": lon,
                     "inactive": bool(entry.get("inactive"))})

    if not rows:
        raise RegionError("RoValra datacenter list was empty")

    rows.sort(key=lambda r: r["label"].lower())
    _cache_write(DATACENTERS_CACHE, rows)
    log.debug(f"Loaded {len(rows)} datacenter regions")
    return rows


def region_counts(place_id):
    try:
        raw = _get(f"{ROVALRA}/v1/servers/counts?place_id={place_id}")
    except Exception as e:
        log.debug(f"Region counts unavailable: {e}")
        return {}

    detailed = (raw.get("counts") or {}).get("detailed_regions") or {}
    counts = {}
    for key, info in detailed.items():
        country = str(key).split("-", 1)[0]
        for city, count in (info.get("cities") or {}).items():
            label = _label(city, country)
            if label:
                counts[label] = counts.get(label, 0) + int(count or 0)
    return counts


def user_location(refresh=False):
    if not refresh:
        cached = _cache_read(LOCATION_CACHE, LOCATION_TTL)
        if cached:
            return cached

    raw = _get(IPINFO_URL, timeout=10)
    parts = str(raw.get("loc") or "").split(",")
    lat, lon = float(parts[0]), float(parts[1])
    item = {"lat": lat, "lon": lon,
            "city": (raw.get("city") or "").strip(),
            "country": (raw.get("country") or "").strip()}
    _cache_write(LOCATION_CACHE, item)
    return item


def _haversine(lat1, lon1, lat2, lon2):
    radius = 6371.0
    to_rad = math.radians

    dlat = to_rad(lat2 - lat1)
    dlon = to_rad(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(to_rad(lat1)) * math.cos(to_rad(lat2))
         * math.sin(dlon / 2) ** 2)
    return 2 * radius * math.asin(math.sqrt(a))


def nearest_regions(limit=6):
    loc = user_location()
    ranked = []
    for dc in datacenters():
        if dc["lat"] is None or dc["inactive"]:
            continue
        ranked.append((_haversine(loc["lat"], loc["lon"], dc["lat"], dc["lon"]),
                       dc["label"]))
    ranked.sort()

    out, seen = [], set()
    for _dist, label in ranked:
        if label in seen:
            continue
        seen.add(label)
        out.append(label)
        if len(out) >= limit:
            break
    return out


def public_servers(place_id, pages=MAX_PAGES):
    found = {}
    cursor = ""
    for page in range(pages):
        url = (f"{ROBLOX_GAMES}/games/{place_id}/servers/Public"
               f"?limit={PAGE_LIMIT}&sortOrder=Asc")
        if cursor:
            url += f"&cursor={urllib.parse.quote(cursor)}"

        try:
            data = _get(url)
        except RegionError as e:
            if page == 0 or not found:
                raise
            log.debug(f"Stopped paging servers after {page} pages: {e}")
            break

        for srv in data.get("data") or []:
            sid = srv.get("id")
            if not sid:
                continue
            found[sid] = {"id": sid,
                          "ping": srv.get("ping"),
                          "playing": srv.get("playing"),
                          "max": srv.get("maxPlayers")}

        cursor = data.get("nextPageCursor") or ""
        if not cursor:
            break

    return found


def annotate(place_id, ids):
    ids = list(ids)
    out = {}
    for start in range(0, len(ids), 50):
        chunk = ids[start:start + 50]
        url = (f"{ROVALRA}/v1/servers/details?place_id={place_id}"
               f"&server_ids={','.join(chunk)}")
        try:
            data = _get(url)
        except Exception as e:
            log.debug(f"Server details failed for {len(chunk)} ids: {e}")
            continue
        for srv in data.get("servers") or []:
            sid = srv.get("server_id")
            if not sid:
                continue
            out[sid] = {
                "city": srv.get("city"),
                "region": srv.get("region"),
                "country": srv.get("country"),
                "country_code": (srv.get("region_code") or "").strip(),
                "first_seen": srv.get("first_seen"),
            }
    return out


def region_servers(place_id, label, max_servers=300):
    city, _, country = label.partition(",")
    params = {"place_id": place_id, "limit": PAGE_LIMIT}
    if city.strip():
        params["city"] = city.strip()
    if country.strip():
        params["country"] = country.strip()

    out = {}
    cursor = 0
    while len(out) < max_servers:
        query = dict(params, cursor=cursor)
        data = _get(f"{ROVALRA}/v1/servers/region?{urllib.parse.urlencode(query)}")
        servers = data.get("servers") or []
        for srv in servers:
            sid = srv.get("server_id")
            if not sid:
                continue
            out[sid] = {
                "city": srv.get("city"),
                "region": srv.get("region"),
                "country": srv.get("country"),
                "country_code": (srv.get("region_code") or "").strip(),
                "first_seen": srv.get("first_seen"),
            }
        if not servers:
            break
        nxt = data.get("next_cursor")
        if not isinstance(nxt, int) or nxt == cursor:
            break
        cursor = nxt

    return out


def _row(sid, pub, meta):
    meta = meta or {}
    ping = pub.get("ping") if pub else None
    return {
        "id": sid,
        "ping": ping,
        "playing": pub.get("playing") if pub else None,
        "max": pub.get("max") if pub else None,
        "region": (_label(meta.get("city"), meta.get("country_code"))
                   or meta.get("country") or "Unknown"),
        "first_seen": meta.get("first_seen"),
    }


def find_servers(place_id, region=ANY_REGION, pages=MAX_PAGES):
    pubs = public_servers(place_id, pages)
    if not pubs:
        raise RegionError("Roblox returned no servers for this place")

    target = region
    if region == AUTO_REGION:
        nearest = nearest_regions(limit=1)
        target = nearest[0] if nearest else ANY_REGION
        log.info(f"Auto region picked {target}")

    rows = []
    if target == ANY_REGION:
        info = annotate(place_id, list(pubs))
        for sid, pub in pubs.items():
            rows.append(_row(sid, pub, info.get(sid)))
    else:
        regional = region_servers(place_id, target)
        for sid, meta in regional.items():
            rows.append(_row(sid, pubs.get(sid), meta))
        if len(rows) < 20:
            info = annotate(place_id, list(pubs))
            have = {r["id"] for r in rows}
            for sid, pub in pubs.items():
                if sid in have:
                    continue
                meta = info.get(sid) or {}
                if _label(meta.get("city"), meta.get("country_code")) == target:
                    rows.append(_row(sid, pub, meta))

        log.info(f"Region {target}: {len(rows)} servers")

    rows.sort(key=lambda r: (r["ping"] is None, r["ping"] if r["ping"] is not None else 0))
    return rows[:MAX_ROWS]


def join_url(place_id, job_id=None):
    url = f"roblox://experiences/start?placeId={place_id}"
    if job_id:
        url += f"&gameInstanceId={job_id}"
    return url


def age_text(first_seen):
    if not first_seen:
        return ""
    try:
        stamp = datetime.fromisoformat(str(first_seen).replace("Z", "+00:00"))
    except ValueError:
        return ""
    seconds = max(0, int(time.time() - stamp.timestamp()))
    if seconds < 60:
        return "just now"
    if seconds < 3600:
        return f"{seconds // 60}m old"
    if seconds < 86400:
        return f"{seconds // 3600}h old"
    return f"{seconds // 86400}d old"


def region_options(place_id, refresh=False):
    options = [ANY_REGION, AUTO_REGION]
    counts = {}
    try:
        counts = region_counts(place_id) if place_id else {}
    except Exception:
        counts = {}

    if counts:
        rows = sorted(counts, key=lambda k: (-counts[k], k.lower()))
        options += [f"{label} ({counts[label]})" for label in rows]
        return options

    try:
        options += [dc["label"] for dc in datacenters(refresh=refresh)
                    if not dc["inactive"]]
    except Exception as e:
        log.debug(f"Falling back to no regions: {e}")
    return options


def strip_count(label):
    if label.endswith(")") and "(" in label:
        return label.rsplit("(", 1)[0].strip()
    return label
