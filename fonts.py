# fonts are complicated as shit bro
# fr

from genericpath import exists
from pathlib import Path
import shutil
import zipfile
import sys
import hashlib

SOBER_APP_ID = "org.vinegarhq.Sober"
SOBER_BASE = Path.home() / ".var/app" / SOBER_APP_ID / "data/sober"
APK_DIR = SOBER_BASE / "packages/x86_64/com.roblox.client"
OVERLAY_FONT_DIR = SOBER_BASE / "asset_overlay/content/fonts"

CONFIG_BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
CONFIG_FILE = CONFIG_BASE / "ui.md"

INSTALLED_FONTS_DIR = Path.home() / ".local" / "share" / "Lution" / "installed_font"

def _calculate_sha256_checksum(apk_path: Path):
    with open(apk_path, "rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def _needs_update() -> bool:
    apk_path = _find_apk()

    if apk_path == None: return False

    last_sober_apk_checksum = ""

    for raw_line in Path(CONFIG_FILE).read_text().splitlines():
        line = raw_line.strip()

        if not line.startswith("LastAPKChecksum = "): continue

        last_sober_apk_checksum = line[len("LastAPKChecksum = "):].strip()

    if last_sober_apk_checksum == "":
        return False
    else:
        hash = hashlib.sha256()

        with open(apk_path, "rb"):
            hash = _calculate_sha256_checksum(apk_path)

            return hash != last_sober_apk_checksum


def _update_apk_checksum():
    apk_path = _find_apk()

    if apk_path == None: return

    hash = _calculate_sha256_checksum(apk_path)

    checksum_location = None
    whole_config = Path(CONFIG_FILE).read_text().splitlines()

    for i, raw_line in enumerate(whole_config):
        line = raw_line.strip()

        if not line.startswith("LastAPKChecksum = "): continue

        checksum_location = i

    if checksum_location != None:
        with open(CONFIG_FILE, "w") as f:
            whole_config[checksum_location] = f"LastAPKChecksum = {hash}"
            _ = f.write("\n".join(whole_config))

        return

    with open(CONFIG_FILE, "a") as f:
        _ = f.write(f"\n# Fonts\nLastAPKChecksum = {hash}")

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

    _update_apk_checksum()

def apply_font_updates():
    if not _needs_update(): return

    if not INSTALLED_FONTS_DIR.exists(): return

    candidates = sorted(INSTALLED_FONTS_DIR.glob("*"), key=lambda p: p.stat().st_ctime)
    if not candidates: return
    target_font = candidates[0]

    try:
        apply_font(str(target_font))
        _update_apk_checksum()
        print("Succesfully updated fonts!")
    except FileNotFoundError:
        print("Could not update fonts :(")
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
    names = []
    with zipfile.ZipFile(apk) as zf:
        for entry in zf.namelist():
            if entry.startswith("assets/content/fonts/") and not entry.startswith("assets/content/fonts/families/"):
                name = Path(entry).name
                if name and Path(name).suffix.lower() in {".ttf", ".otf"}:
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
    shutil.rmtree(OVERLAY_FONT_DIR)
    return True
