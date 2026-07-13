# fonts are complicated as shit bro

from pathlib import Path
import shutil
import zipfile

SOBER_APP_ID = "org.vinegarhq.Sober"
SOBER_BASE = Path.home() / ".var/app" / SOBER_APP_ID / "data/sober"
APK_DIR = SOBER_BASE / "packages/x86_64/com.roblox.client"
OVERLAY_FONT_DIR = SOBER_BASE / "asset_overlay/content/fonts"


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
