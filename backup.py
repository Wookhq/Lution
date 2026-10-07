# backup for both sober and lution so you can get the exact same setup fast
from pathlib import Path
import shutil
import zipfile

import paths

OVERLAY_DIR = paths.LUTION_OVERLAY
LUTION_CONFIG = paths.LUTION_CONFIG
STATE_DIR = paths.STATE_DIR
MODS_DIR = paths.STATE_DIR / "Mods"

INSTALLED_DIRS = {
    name: paths.LUTION_ROOT / name
    for name in ("installed_font", "installed_emoji",
                 "installed_cursors", "installed_sounds")
}


def _add_tree(zf, src, arc_root):
    for fp in src.rglob("*"):
        if fp.is_file():
            zf.write(fp, arc_root + "/" + str(fp.relative_to(src)))


def _extract(zf, member, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zf.open(member) as src, open(dest, "wb") as dst:
        dst.write(src.read())


def export_backup(backup_path):
    backup_path = Path(backup_path)
    if not backup_path.suffix:
        backup_path = backup_path.with_suffix(".zip")

    with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
        if OVERLAY_DIR.exists():
            _add_tree(zf, OVERLAY_DIR, "asset_overlay")

        for arc_root, src in INSTALLED_DIRS.items():
            if src.exists():
                _add_tree(zf, src, "installed/" + arc_root)

        if LUTION_CONFIG.exists():
            zf.write(LUTION_CONFIG, "config.json")

        if STATE_DIR.exists():
            _add_tree(zf, STATE_DIR, "lution")

        if MODS_DIR.exists():
            for fp in MODS_DIR.glob("*.zip"):
                zf.write(fp, "mods/" + fp.name)

    return backup_path


def import_backup(backup_path):
    backup_path = Path(backup_path)
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup not found: {backup_path}")

    roots = [("asset_overlay/", OVERLAY_DIR),
             ("installed/", paths.LUTION_ROOT),
             ("lution/", STATE_DIR),
             ("mods/", MODS_DIR)]

    restored = []
    with zipfile.ZipFile(backup_path, "r") as zf:
        for member in zf.namelist():
            if member.endswith("/"):
                continue

            if member == "config.json":
                _extract(zf, member, LUTION_CONFIG)
                restored.append(member)
                continue

            for prefix, dest_root in roots:
                if member.startswith(prefix):
                    _extract(zf, member, dest_root / member[len(prefix):])
                    restored.append(member)
                    break

    return restored


def reset_all():
    removed = []
    if OVERLAY_DIR.exists():
        shutil.rmtree(OVERLAY_DIR)
        removed.append("overlay")

    for name, src in INSTALLED_DIRS.items():
        if src.exists():
            shutil.rmtree(src)
            removed.append(name)

    if LUTION_CONFIG.exists():
        LUTION_CONFIG.unlink()
        removed.append("config")

    if STATE_DIR.exists():
        shutil.rmtree(STATE_DIR)
        removed.append("lution state")

    paths.ensure_lution_dirs()
    return removed
