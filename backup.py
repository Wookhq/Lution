# backup for both sober and lution so you can get the exact same setup fast
from pathlib import Path
import shutil
import zipfile
import json
import os

SOBER_APP_ID = "org.vinegarhq.Sober"
SOBER_BASE = Path.home() / ".var/app" / SOBER_APP_ID / "data/sober"
OVERLAY_DIR = SOBER_BASE / "asset_overlay"
SOBER_CONFIG = SOBER_BASE.parent.parent / "config/sober/config.json"
LUTION_DIR = Path.home() / ".local/Lution"
MODS_DIR = Path.home() / ".local/Lution/Mods"


def export_backup(backup_path):
    backup_path = Path(backup_path)
    if not backup_path.suffix:
        backup_path = backup_path.with_suffix(".zip")

    with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
        if OVERLAY_DIR.exists():
            for root, dirs, files in os.walk(OVERLAY_DIR):
                for f in files:
                    fp = Path(root) / f
                    arcname = "asset_overlay/" + str(fp.relative_to(OVERLAY_DIR))
                    zf.write(fp, arcname)

        if SOBER_CONFIG.exists():
            zf.write(SOBER_CONFIG, "config.json")

        if LUTION_DIR.exists():
            for fp in LUTION_DIR.rglob("*"):
                if fp.is_file():
                    arcname = "lution/" + str(fp.relative_to(LUTION_DIR))
                    zf.write(fp, arcname)

        if MODS_DIR.exists():
            for fp in MODS_DIR.glob("*.zip"):
                zf.write(fp, "mods/" + fp.name)

    return backup_path


def import_backup(backup_path):
    backup_path = Path(backup_path)
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup not found: {backup_path}")

    restored = []
    with zipfile.ZipFile(backup_path, "r") as zf:
        for member in zf.namelist():
            if member.startswith("asset_overlay/"):
                rel = member[len("asset_overlay/"):]
                dest = OVERLAY_DIR / rel
                if member.endswith("/"):
                    dest.mkdir(parents=True, exist_ok=True)
                else:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(member) as src, open(dest, "wb") as dst:
                        dst.write(src.read())
                restored.append(member)

            elif member == "config.json":
                dest = SOBER_CONFIG
                dest.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as src, open(dest, "wb") as dst:
                    dst.write(src.read())
                restored.append(member)

            elif member.startswith("lution/"):
                rel = member[len("lution/"):]
                dest = LUTION_DIR / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as src, open(dest, "wb") as dst:
                    dst.write(src.read())
                restored.append(member)

            elif member.startswith("mods/"):
                rel = member[len("mods/"):]
                dest = MODS_DIR / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as src, open(dest, "wb") as dst:
                    dst.write(src.read())
                restored.append(member)

    return restored


def reset_all():
    removed = []
    if OVERLAY_DIR.exists():
        shutil.rmtree(OVERLAY_DIR)
        removed.append("asset_overlay")
    if LUTION_DIR.exists():
        shutil.rmtree(LUTION_DIR)
        removed.append("lution config")
    return removed
