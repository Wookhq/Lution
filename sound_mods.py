# customizing roblox sounds

from pathlib import Path
import shutil
import sys

SOBER_APP_ID = "org.vinegarhq.Sober"
SOBER_BASE = Path.home() / ".var/app" / SOBER_APP_ID / "data/sober"
OVERLAY_SOUNDS_DIR = SOBER_BASE / "asset_overlay/content/sounds"

BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))

SOUND_STATES = [
    "oof.ogg",
    "action_jump.mp3",
    "action_jump_land.mp3",
    "action_falling.ogg",
    "action_get_up.mp3",
    "action_swim.mp3",
    "action_footsteps_plastic.mp3",
    "impact_water.mp3",
    "impact_explosion_03.mp3",
    "volume_slider.ogg",
]

INSTALLED_SOUNDS_DIR = Path.home() / ".local" / "share" / "Lution" / "installed_sounds"


def apply_sounds(sounds_dict):

    OVERLAY_SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
    applied = []
    for name in SOUND_STATES:
        source = sounds_dict.get(name)
        if source is None:
            continue
        source = Path(source)
        if not source.exists():
            continue
        dest = OVERLAY_SOUNDS_DIR / name
        shutil.copyfile(source, dest)
        applied.append(name)
    return applied


def restore_sounds():
    removed = []
    for name in SOUND_STATES:
        target = OVERLAY_SOUNDS_DIR / name
        if target.exists():
            target.unlink()
            removed.append(name)
    if INSTALLED_SOUNDS_DIR.exists():
        shutil.rmtree(INSTALLED_SOUNDS_DIR)
    return removed


def save_installed_sounds(sounds_dict):
    if not INSTALLED_SOUNDS_DIR.exists():
        INSTALLED_SOUNDS_DIR.mkdir(exist_ok=True, parents=True)

    for name in SOUND_STATES:
        source = sounds_dict.get(name)
        dest = INSTALLED_SOUNDS_DIR / name
        if source is None:
            if dest.exists():
                dest.unlink()
            continue
        source = Path(source)
        if not source.exists():
            continue
        shutil.copyfile(source, dest)


def reapply_sounds():
    if not INSTALLED_SOUNDS_DIR.exists():
        return

    sounds_dict = {}
    for name in SOUND_STATES:
        path = INSTALLED_SOUNDS_DIR / name
        if path.exists():
            sounds_dict[name] = str(path)
    if not sounds_dict:
        return

    try:
        apply_sounds(sounds_dict)
    except FileNotFoundError:
        return
