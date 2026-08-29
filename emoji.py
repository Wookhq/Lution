# this what replaces emoji font

from pathlib import Path
import shutil
import sys

SOBER_APP_ID = "org.vinegarhq.Sober"
SOBER_BASE = Path.home() / ".var/app" / SOBER_APP_ID / "data/sober"
APK_DIR = SOBER_BASE / "packages/x86_64/com.roblox.client"
OVERLAY_FONT_DIR = SOBER_BASE / "asset_overlay/content/fonts"

EMOJI_FONT_NAMES = ["RobloxEmoji.ttf", "TwemojiMozilla.ttf"]

BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
PRESETS_DIR = BASE / "emoji_presets"
INSTALLED_EMOJI_DIR = Path.home() / ".local" / "share" / "Lution" / "installed_emoji"


def list_presets():
    if not PRESETS_DIR.exists():
        return []
    return sorted([f.stem for f in PRESETS_DIR.glob("*.ttf")])


def get_preset_path(name):
    path = PRESETS_DIR / f"{name}.ttf"
    return str(path) if path.exists() else None


def apply_emoji(source_path):
    source_path = Path(source_path)
    if not source_path.exists():
        raise FileNotFoundError(f"Emoji font file not found: {source_path}")

    OVERLAY_FONT_DIR.mkdir(parents=True, exist_ok=True)
    replaced = []
    for name in EMOJI_FONT_NAMES:
        dest = OVERLAY_FONT_DIR / name
        shutil.copyfile(source_path, dest)
        replaced.append(str(dest))
    return replaced


def restore_emoji():
    removed = []
    for name in EMOJI_FONT_NAMES:
        target = OVERLAY_FONT_DIR / name
        if target.exists():
            target.unlink()
            removed.append(name)
    if INSTALLED_EMOJI_DIR.exists():
        shutil.rmtree(INSTALLED_EMOJI_DIR)
    return removed


def save_installed_emoji(font_path: Path | str) -> None:
    if isinstance(font_path, str):
        font_path = Path(font_path)

    if not INSTALLED_EMOJI_DIR.exists():
        INSTALLED_EMOJI_DIR.mkdir(exist_ok=True, parents=True)

    dest_file = INSTALLED_EMOJI_DIR / ("emoji" + font_path.suffix)
    try:
        shutil.copy(font_path, dest_file, follow_symlinks=True)
    except shutil.SameFileError:
        pass


def reapply_emoji():
    if not INSTALLED_EMOJI_DIR.exists():
        return

    candidates = sorted(INSTALLED_EMOJI_DIR.glob("*"), key=lambda p: p.stat().st_ctime)
    if not candidates:
        return

    try:
        apply_emoji(str(candidates[0]))
    except FileNotFoundError:
        return
