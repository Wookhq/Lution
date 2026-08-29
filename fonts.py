# fonts are complicated as shit bro
# fr
# yes bro
from genericpath import exists
from pathlib import Path
import shutil
import zipfile
import sys

import emoji
import log

SOBER_APP_ID = "org.vinegarhq.Sober"
SOBER_BASE = Path.home() / ".var/app" / SOBER_APP_ID / "data/sober"
APK_DIR = SOBER_BASE / "packages/x86_64/com.roblox.client"
OVERLAY_FONT_DIR = SOBER_BASE / "asset_overlay/content/fonts"

INSTALLED_FONTS_DIR = Path.home() / ".local" / "share" / "Lution" / "installed_font"

def save_installed_font(font_path: Path | str) -> None:
    if isinstance(font_path, str):
        font_path = Path.from_uri("file:"+font_path)

    if not INSTALLED_FONTS_DIR.exists():
        INSTALLED_FONTS_DIR.mkdir(exist_ok=True, parents=True)

    dest_file = INSTALLED_FONTS_DIR / ("font"+font_path.suffix)
    try:
        _ = shutil.copy(font_path, dest_file, follow_symlinks=True)
    except shutil.SameFileError:
        return

def reapply_fonts():
    if not INSTALLED_FONTS_DIR.exists(): return

    candidates = sorted(INSTALLED_FONTS_DIR.glob("*"), key=lambda p: p.stat().st_ctime)
    if not candidates: return
    target_font = candidates[0]

    try:
        apply_font(str(target_font))
        log.info("Fonts updated after Sober APK change")
    except FileNotFoundError:
        log.error("Could not update fonts, font file is missing")
        return




def _find_apk():
    if not APK_DIR.exists():
        return None
    candidates = sorted(APK_DIR.glob("*.apk"), key=lambda p: p.stat().st_size, reverse=True)
    return candidates[0] if candidates else None


def _apk_font_names():
    apk = _find_apk()
    if apk is None:
        return []
    emoji_names = {name.lower() for name in emoji.EMOJI_FONT_NAMES}
    names = []
    with zipfile.ZipFile(apk) as zf:
        for entry in zf.namelist():
            if entry.startswith("assets/content/fonts/") and not entry.startswith("assets/content/fonts/families/"):
                name = Path(entry).name
                if name and Path(name).suffix.lower() in {".ttf", ".otf"} and name.lower() not in emoji_names:
                    names.append(name)
    return names


def apply_font(source_path):
    source_path = Path(source_path)
    if not source_path.exists():
        raise FileNotFoundError(f"Font file not found: {source_path}")

    font_names = _apk_font_names()
    if not font_names:
        raise FileNotFoundError(
            "Could not read font list from the Roblox APK. "
            "Make sure Sober is installed and has run at least once."
        )

    OVERLAY_FONT_DIR.mkdir(parents=True, exist_ok=True)
    replaced = []
    for name in font_names:
        dest = OVERLAY_FONT_DIR / name
        shutil.copyfile(source_path, dest)
        replaced.append(str(dest))
    return replaced


def restore_fonts():
    if not OVERLAY_FONT_DIR.exists():
        return False
    emoji_names = {name.lower() for name in emoji.EMOJI_FONT_NAMES}
    removed = False
    for path in OVERLAY_FONT_DIR.iterdir():
        if path.name.lower() in emoji_names:
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        removed = True
    return removed
