# i stole the code from bartender pls don't take this down bartender devs

from pathlib import Path
import shutil
import zipfile
import json
import tempfile

SOBER_APP_ID = "org.vinegarhq.Sober"
SOBER_DATA = Path.home() / ".var/app" / SOBER_APP_ID / "data/sober"
OVERLAY_DIR = SOBER_DATA / "asset_overlay"
MODS_DIR = Path.home() / ".local/Lution/Mods"


def ensure_dirs():
    MODS_DIR.mkdir(parents=True, exist_ok=True)
    OVERLAY_DIR.mkdir(parents=True, exist_ok=True)


def list_mods():
    ensure_dirs()
    return sorted(MODS_DIR.glob("*.zip"), key=lambda p: p.stem.lower())


def import_mod(source_path):
    ensure_dirs()
    source_path = Path(source_path)
    dest = MODS_DIR / source_path.name
    shutil.copy2(source_path, dest)
    return dest


def install_mod(mod_path):
    ensure_dirs()
    mod_path = Path(mod_path)
    if not mod_path.exists():
        return False, f"Mod file not found: {mod_path.name}"

    temp_dir = Path(tempfile.mkdtemp(prefix="lution_mod_"))
    try:
        with zipfile.ZipFile(mod_path, "r") as zf:
            zf.extractall(temp_dir)

        content_dir = _find_content_dir(temp_dir)
        if content_dir is None:
            return False, (
                "Invalid mod structure.\n"
                "Mod archive must contain a 'content' or 'ExtraContent' directory."
            )

        copied = []
        for name in ("content", "ExtraContent"):
            src = content_dir / name
            dest = OVERLAY_DIR / name
            if src.exists():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(src, dest)
                copied.append(name)

        if not copied:
            return False, "No valid content found in mod archive."

        return True, f"Installed {mod_path.name}"
    except Exception as e:
        return False, f"Failed to install: {e}"
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def remove_mod_content():
    ensure_dirs()
    removed = []
    for name in ("content", "ExtraContent"):
        target = OVERLAY_DIR / name
        if target.exists():
            shutil.rmtree(target)
            removed.append(name)
    return removed


def delete_mod(mod_path):
    mod_path = Path(mod_path)
    if mod_path.exists():
        mod_path.unlink()
        return True
    return False


def _find_content_dir(base_dir):
    if any((base_dir / n).exists() for n in ("content", "ExtraContent")):
        return base_dir
    for item in base_dir.iterdir():
        if item.is_dir() and any((item / n).exists() for n in ("content", "ExtraContent")):
            return item
    return None
