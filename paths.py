# where everything lives

import shutil
import zipfile
from pathlib import Path

import log

SOBER_APP_ID = "org.vinegarhq.Sober"

_APP_DIR = Path.home() / ".var/app" / SOBER_APP_ID
SOBER_DATA = _APP_DIR / "data/sober"
SOBER_OVERLAY = SOBER_DATA / "asset_overlay"
SOBER_CONFIG = _APP_DIR / "config/sober/config.json"
SOBER_APK_DIR = SOBER_DATA / "packages/x86_64/com.roblox.client"

LUTION_ROOT = Path.home() / ".local/share/Lution"
LUTION_OVERLAY = LUTION_ROOT / "overlay"
LUTION_CONFIG = LUTION_ROOT / "sober_config.json"

STATE_DIR = Path.home() / ".local/Lution"

OVERLAY_ROOTS = ("content", "ExtraContent", "PlatformContent")

FONT_DIRS = {
    "font": LUTION_ROOT / "installed_font",
    "emoji": LUTION_ROOT / "installed_emoji",
    "cursors": LUTION_ROOT / "installed_cursors",
    "sounds": LUTION_ROOT / "installed_sounds",
}


def lution_overlay_dir(name):
    return LUTION_OVERLAY / name


def sober_overlay_dir(name):
    return SOBER_OVERLAY / name


def ensure_lution_dirs():
    for name in OVERLAY_ROOTS:
        (LUTION_OVERLAY / name).mkdir(parents=True, exist_ok=True)
    LUTION_ROOT.mkdir(parents=True, exist_ok=True)


def apk_has_font_assets(apk_path):
    try:
        with zipfile.ZipFile(apk_path) as zf:
            for entry in zf.namelist():
                if entry.startswith("assets/content/fonts/"):
                    return True
    except (OSError, zipfile.BadZipFile):
        pass
    return False


def find_base_apk():
    if not SOBER_APK_DIR.exists():
        return None

    apks = list(SOBER_APK_DIR.glob("*.apk"))
    if not apks:
        return None

    for apk in apks:
        if apk.name == "base.apk":
            return apk

    with_assets = [a for a in apks if apk_has_font_assets(a)]
    pool = with_assets or apks
    return max(pool, key=lambda p: p.stat().st_size)


def _zip_dir(src, arc_root, zf):
    for fp in src.rglob("*"):
        if fp.is_file():
            zf.write(fp, arc_root + "/" + str(fp.relative_to(src)))


def migrate_legacy_overlay():
    ensure_lution_dirs()

    pending = []
    for name in OVERLAY_ROOTS:
        src = SOBER_OVERLAY / name
        if not src.exists():
            continue
        if any(p.is_file() for p in src.rglob("*")):
            pending.append((name, src))

    if not pending:
        return []

    backup_zip = LUTION_ROOT / "pre_migration_overlay.zip"
    with zipfile.ZipFile(backup_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, src in pending:
            _zip_dir(src, "asset_overlay/" + name, zf)
    log.info(f"Backed up existing overlay to {backup_zip}")

    migrated = []
    for name, src in pending:
        dest = LUTION_OVERLAY / name
        shutil.copytree(src, dest, dirs_exist_ok=True)
        shutil.rmtree(src)
        migrated.append(name)
        log.info(f"Migrated asset_overlay/{name} into lution")

    return migrated


def cleanup_legacy_config():
    return not SOBER_CONFIG.exists()
