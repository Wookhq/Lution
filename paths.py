# where everything lives

import shutil
import sys
import zipfile
from pathlib import Path

SOBER_APP_ID = "org.vinegarhq.Sober"

_APP_DIR = Path.home() / ".var/app" / SOBER_APP_ID
SOBER_DATA = _APP_DIR / "data/sober"
SOBER_OVERLAY = SOBER_DATA / "asset_overlay"
SOBER_CONFIG = _APP_DIR / "config/sober/config.json"
SOBER_APK_DIR = SOBER_DATA / "packages/x86_64/com.roblox.client"

LUTION_ROOT = Path.home() / ".local/share/Lution"
LUTION_OVERLAY = SOBER_OVERLAY
LUTION_CONFIG = SOBER_CONFIG

STATE_DIR = LUTION_ROOT
LEGACY_STATE_DIR = Path.home() / ".local/Lution"

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


def _unique_old(path):
    candidate = path.with_name(path.name + ".old")
    index = 1
    while candidate.exists() or candidate.is_symlink():
        candidate = path.with_name(f"{path.name}.old.{index}")
        index += 1
    return candidate


def _merge_path(src, dst):
    if (src.is_dir() and not src.is_symlink()
            and dst.is_dir() and not dst.is_symlink()):
        for child in list(src.iterdir()):
            _merge_path(child, dst / child.name)
        try:
            src.rmdir()
        except OSError:
            pass
        return

    if dst.exists() or dst.is_symlink():
        try:
            src_mtime = src.lstat().st_mtime_ns
            dst_mtime = dst.lstat().st_mtime_ns
        except OSError:
            src_mtime = dst_mtime = 0
        if src_mtime > dst_mtime:
            shutil.move(str(dst), str(_unique_old(dst)))
            shutil.move(str(src), str(dst))
        else:
            shutil.move(str(src), str(_unique_old(dst)))
        return

    shutil.move(str(src), str(dst))


def _migrate_legacy_state():
    if (LEGACY_STATE_DIR == STATE_DIR or LEGACY_STATE_DIR.is_symlink()
            or not LEGACY_STATE_DIR.is_dir()):
        return
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        for child in list(LEGACY_STATE_DIR.iterdir()):
            _merge_path(child, STATE_DIR / child.name)
        try:
            LEGACY_STATE_DIR.rmdir()
        except OSError:
            pass
    except OSError as e:
        print(f"lution warning: could not migrate {LEGACY_STATE_DIR} "
              f"to {STATE_DIR}: {e}", file=sys.stderr)


_migrate_legacy_state()
