# change cursor and also reapply when sober updates

from pathlib import Path
import shutil
import sys

SOBER_APP_ID = "org.vinegarhq.Sober"
SOBER_BASE = Path.home() / ".var/app" / SOBER_APP_ID / "data/sober"
OVERLAY_TEXTURE_DIR = SOBER_BASE / "asset_overlay/content/textures/Cursors/KeyboardMouse"

BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
PRESETS_DIR = BASE / "cursor_presets"

CURSOR_STATES = ["ArrowCursor", "ArrowFarCursor", "IBeamCursor"]

INSTALLED_CURSORS_DIR = Path.home() / ".local" / "share" / "Lution" / "installed_cursors"


def list_presets():
    if not PRESETS_DIR.exists():
        return []
    return sorted([d.name for d in PRESETS_DIR.iterdir() if d.is_dir()])


def get_preset_cursors(preset_name):
    preset_dir = PRESETS_DIR / preset_name
    if not preset_dir.exists():
        return {}
    cursors = {}
    for name in CURSOR_STATES:
        path = preset_dir / f"{name}.png"
        if path.exists():
            cursors[name] = str(path)
    return cursors


def apply_cursors(cursors_dict):
    OVERLAY_TEXTURE_DIR.mkdir(parents=True, exist_ok=True)
    applied = []
    for name in CURSOR_STATES:
        source = cursors_dict.get(name)
        if source is None:
            continue
        source = Path(source)
        if not source.exists():
            continue
        dest = OVERLAY_TEXTURE_DIR / f"{name}.png"
        shutil.copyfile(source, dest)
        applied.append(name)
    return applied


def restore_cursors():
    removed = []
    for name in CURSOR_STATES:
        target = OVERLAY_TEXTURE_DIR / f"{name}.png"
        if target.exists():
            target.unlink()
            removed.append(name)
    if INSTALLED_CURSORS_DIR.exists():
        shutil.rmtree(INSTALLED_CURSORS_DIR)
    return removed


def save_installed_cursors(cursors_dict):
    if not INSTALLED_CURSORS_DIR.exists():
        INSTALLED_CURSORS_DIR.mkdir(exist_ok=True, parents=True)

    for name in CURSOR_STATES:
        source = cursors_dict.get(name)
        dest = INSTALLED_CURSORS_DIR / f"{name}.png"
        if source is None:
            if dest.exists():
                dest.unlink()
            continue
        source = Path(source)
        if not source.exists():
            continue
        shutil.copyfile(source, dest)


def reapply_cursors():
    if not INSTALLED_CURSORS_DIR.exists():
        return

    cursors_dict = {}
    for name in CURSOR_STATES:
        path = INSTALLED_CURSORS_DIR / f"{name}.png"
        if path.exists():
            cursors_dict[name] = str(path)
    if not cursors_dict:
        return

    try:
        apply_cursors(cursors_dict)
    except FileNotFoundError:
        return
