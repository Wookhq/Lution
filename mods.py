# i stole the code from bartender pls don't take this down bartender devs

from pathlib import Path
import shutil
import zipfile
import json
import tempfile
import os

SOBER_APP_ID = "org.vinegarhq.Sober"
SOBER_DATA = Path.home() / ".var/app" / SOBER_APP_ID / "data/sober"
OVERLAY_DIR = SOBER_DATA / "asset_overlay"
MODS_DIR = Path.home() / ".local/Lution/Mods"

MANIFEST_FILE = Path.home() / ".local/Lution/mods_manifest.json"

def _load_manifest():
    try:
        data = json.loads(MANIFEST_FILE.read_text())
        return data if isinstance(data, list) else []
    except Exception:
        return []

def _save_manifest(names):
    MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_FILE.write_text(json.dumps(names))

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

def _mod_file_list(mod_path):
    files = set()
    try:
        with zipfile.ZipFile(mod_path, "r") as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                name = info.filename
                for prefix in ("content/", "ExtraContent/", "PlatformContent/"):
                    if prefix in name:
                        idx = name.index(prefix)
                        files.add(name[idx:])
                        break
    except Exception:
        pass
    return files

# this is very useful so two mods don't literally replace ur cursor or any asset at the same time
def check_mod_conflicts(mod_path):
    mod_files = _mod_file_list(mod_path)
    if not mod_files:
        return []

    conflicts = []
    for rel in mod_files:
        target = OVERLAY_DIR / rel
        if target.exists():
            conflicts.append(rel)
    return conflicts

def scan_all_conflicts():
    mods = list_mods()
    if len(mods) < 2:
        return {}

    mod_files = {}
    for mod in mods:
        mod_files[mod.stem] = _mod_file_list(mod)

    conflicts = {}
    names = list(mod_files.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            overlap = mod_files[names[i]] & mod_files[names[j]]
            if overlap:
                conflicts[(names[i], names[j])] = sorted(overlap)
    return conflicts

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
        for name in CONTENT_ROOTS:
            src = content_dir / name
            if not src.exists():
                continue
            dest = OVERLAY_DIR / name
            for root, _dirs, files in os.walk(src):
                rel = Path(root).relative_to(src)
                target_dir = dest if str(rel) == "." else dest / rel
                target_dir.mkdir(parents=True, exist_ok=True)
                for f in files:
                    shutil.copy2(Path(root) / f, target_dir / f)
            copied.append(name)

        if not copied:
            return False, "No valid content found in mod archive."

        name = mod_path.name
        installed = _load_manifest()
        if name in installed:
            installed.remove(name)
        installed.append(name)
        _save_manifest(installed)

        return True, f"Installed {mod_path.name}"
    except Exception as e:
        return False, f"Failed to install: {e}"
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def remove_mod_content(include_custom=False):
    ensure_dirs()
    removed = []

    PROTECTED = {
        OVERLAY_DIR / "content" / "textures" / "Cursors" / "KeyboardMouse",
        OVERLAY_DIR / "content" / "fonts",
        OVERLAY_DIR / "content" / "sounds",
    }

    for name in CONTENT_ROOTS:
        top = OVERLAY_DIR / name
        if not top.exists():
            continue
        if include_custom:
            shutil.rmtree(top)
            removed.append(name)
            continue
        for root, dirs, files in os.walk(top):
            root_path = Path(root)
            if any(root_path == p or p in root_path.parents for p in PROTECTED):
                continue
            for f in files:
                (root_path / f).unlink()
            for d in dirs:
                dir_path = root_path / d
                if not any(dir_path == p or p in dir_path.parents for p in PROTECTED):
                    shutil.rmtree(dir_path)

        if not any(top.rglob("*")):
            shutil.rmtree(top)
        removed.append(name)

    _save_manifest([])

    return removed

def delete_mod(mod_path):
    mod_path = Path(mod_path)
    if mod_path.exists():
        mod_path.unlink()
        manifest = [n for n in _load_manifest() if n != mod_path.name]
        _save_manifest(manifest)
        return True
    return False

def reapply_mods():
    for name in _load_manifest():
        mod_path = MODS_DIR / name
        if mod_path.exists():
            install_mod(mod_path)

CONTENT_ROOTS = ("content", "ExtraContent", "PlatformContent")

def _find_content_dir(base_dir):
    if any((base_dir / n).exists() for n in CONTENT_ROOTS):
        return base_dir
    for item in base_dir.iterdir():
        if item.is_dir() and any((item / n).exists() for n in CONTENT_ROOTS):
            return item
    return None
