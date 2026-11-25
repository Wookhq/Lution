# easy emote wheel customization

from pathlib import Path
import shutil
import sys

import paths
import sync

OVERLAY_EMOTE_DIR = paths.LUTION_OVERLAY / "content/textures/ui/Emotes/TenFoot"

BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
PRESETS_DIR = BASE / "emote_presets"

SCALES = ["", "@2x", "@3x"]

WHEEL_PARTS = ["CircleBackground", "SegmentedCircle",
               "SelectedGradient", "SelectedLine"]

PART_LABELS = {
    "CircleBackground": "Wheel background",
    "SegmentedCircle": "Wheel segments",
    "SelectedGradient": "Selection glow",
    "SelectedLine": "Selection pointer",
}

INSTALLED_EMOTE_DIR = paths.LUTION_ROOT / "installed_emote_wheel"


def list_presets():
    if not PRESETS_DIR.exists():
        return []
    return sorted([d.name for d in PRESETS_DIR.iterdir() if d.is_dir()])


def get_preset_wheel(preset_name):
    preset_dir = PRESETS_DIR / preset_name
    if not preset_dir.exists():
        return {}
    wheel = {}
    for name in WHEEL_PARTS:
        path = preset_dir / f"{name}.png"
        if path.exists():
            wheel[name] = str(path)
    return wheel


@sync.locked
def apply_wheel(parts_dict):
    OVERLAY_EMOTE_DIR.mkdir(parents=True, exist_ok=True)
    applied = []
    for name in WHEEL_PARTS:
        source = parts_dict.get(name)
        if source is None:
            continue
        source = Path(source)
        if not source.exists():
            continue
        for scale in SCALES:
            shutil.copyfile(source, OVERLAY_EMOTE_DIR / f"{name}{scale}.png")
        applied.append(name)
    return applied


@sync.locked
def restore_wheel():
    removed = []
    for name in WHEEL_PARTS:
        for scale in SCALES:
            target = OVERLAY_EMOTE_DIR / f"{name}{scale}.png"
            if target.exists():
                target.unlink()
                removed.append(name)
    if INSTALLED_EMOTE_DIR.exists():
        shutil.rmtree(INSTALLED_EMOTE_DIR)
    return sorted(set(removed))


@sync.locked
def save_installed_wheel(parts_dict):
    INSTALLED_EMOTE_DIR.mkdir(parents=True, exist_ok=True)

    for name in WHEEL_PARTS:
        dest = INSTALLED_EMOTE_DIR / f"{name}.png"
        source = parts_dict.get(name)
        if source is None:
            if dest.exists():
                dest.unlink()
            continue
        source = Path(source)
        if not source.exists():
            continue
        shutil.copyfile(source, dest)


@sync.locked
def reapply_wheel():
    if not INSTALLED_EMOTE_DIR.exists():
        return

    parts_dict = {}
    for name in WHEEL_PARTS:
        path = INSTALLED_EMOTE_DIR / f"{name}.png"
        if path.exists():
            parts_dict[name] = str(path)
    if not parts_dict:
        return

    apply_wheel(parts_dict)
