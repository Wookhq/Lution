# backup for both sober and lution so you can get the exact same setup fast
from pathlib import Path
import shutil
import zipfile

import paths
import log
import fflags

OVERLAY_DIR = paths.LUTION_OVERLAY
LUTION_CONFIG = paths.LUTION_CONFIG
STATE_DIR = paths.STATE_DIR
MODS_DIR = paths.STATE_DIR / "Mods"

INSTALLED_DIRS = {
    name: paths.LUTION_ROOT / name
    for name in ("installed_font", "installed_emoji",
                 "installed_cursors", "installed_sounds",
                 "installed_emote_wheel")
}

STATE_FILES = (
    "theme.json",
    "env_vars.json",
    "launcher_config.json",
    "fflag_user_presets.json",
    "mods_manifest.json",
    "setup_done.json",
)


def _add_tree(zf, src, arc_root):
    for fp in src.rglob("*"):
        if fp.is_file():
            zf.write(fp, arc_root + "/" + str(fp.relative_to(src)))


def _safe_dest(root, name):
    root = Path(root)
    if Path(name).is_absolute() or name.startswith("\\\\"):
        raise ValueError(f"Backup entry has an absolute path: {name}")
    parts = [p for p in name.replace("\\", "/").split("/") if p]
    if any(p == ".." for p in parts):
        raise ValueError(f"Backup entry escapes its folder: {name}")
    dest = root.joinpath(*parts) if parts else root
    resolved = dest.resolve()
    if resolved != root.resolve() and root.resolve() not in resolved.parents:
        raise ValueError(f"Backup entry resolves outside its folder: {name}")
    return dest


def _extract(zf, member, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zf.open(member) as src, open(dest, "wb") as dst:
        dst.write(src.read())


def export_backup(backup_path):
    backup_path = Path(backup_path)
    if not backup_path.suffix:
        backup_path = backup_path.with_suffix(".zip")

    with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in paths.OVERLAY_ROOTS:
            src = OVERLAY_DIR / name
            if src.exists():
                _add_tree(zf, src, "asset_overlay/" + name)

        for arc_root, src in INSTALLED_DIRS.items():
            if src.exists():
                _add_tree(zf, src, "installed/" + arc_root)

        if LUTION_CONFIG.exists():
            zf.write(LUTION_CONFIG, "config.json")

        for name in STATE_FILES:
            src = STATE_DIR / name
            if src.is_file():
                zf.write(src, "lution/" + name)

        if MODS_DIR.exists():
            for fp in MODS_DIR.glob("*.zip"):
                zf.write(fp, "mods/" + fp.name)

    return backup_path


def import_backup(backup_path):
    backup_path = Path(backup_path)
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup not found: {backup_path}")

    entries = []
    overlay_roots = set()
    installed_roots = set()
    mods_present = False
    state_present = False

    with zipfile.ZipFile(backup_path, "r") as zf:
        for member in zf.namelist():
            if member.endswith("/"):
                continue

            if member == "config.json":
                entries.append((member, LUTION_CONFIG))
                continue

            if member.startswith("asset_overlay/"):
                rest = member[len("asset_overlay/"):]
                top = rest.split("/", 1)[0]
                if top not in paths.OVERLAY_ROOTS:
                    log.warning(f"Skipping unknown overlay entry: {member}")
                    continue
                try:
                    dest = _safe_dest(OVERLAY_DIR, rest)
                except ValueError as e:
                    log.error(f"Skipping unsafe backup entry: {e}")
                    continue
                entries.append((member, dest))
                overlay_roots.add(top)
                continue

            if member.startswith("installed/"):
                rest = member[len("installed/"):]
                top = rest.split("/", 1)[0]
                if top not in INSTALLED_DIRS:
                    log.warning(f"Skipping unknown installed entry: {member}")
                    continue
                try:
                    dest = _safe_dest(paths.LUTION_ROOT, rest)
                except ValueError as e:
                    log.error(f"Skipping unsafe backup entry: {e}")
                    continue
                entries.append((member, dest))
                installed_roots.add(top)
                continue

            if member.startswith("lution/"):
                rest = member[len("lution/"):]
                if rest not in STATE_FILES:
                    log.warning(f"Skipping non-backup state entry: {member}")
                    continue
                entries.append((member, STATE_DIR / rest))
                state_present = True
                continue

            if member.startswith("mods/"):
                rest = member[len("mods/"):]
                if "/" in rest or not rest.endswith(".zip"):
                    log.warning(f"Skipping unknown mod entry: {member}")
                    continue
                try:
                    dest = _safe_dest(MODS_DIR, rest)
                except ValueError as e:
                    log.error(f"Skipping unsafe backup entry: {e}")
                    continue
                entries.append((member, dest))
                mods_present = True
                continue

            log.warning(f"Skipping unknown backup entry: {member}")

    for top in overlay_roots:
        shutil.rmtree(OVERLAY_DIR / top, ignore_errors=True)
    for top in installed_roots:
        shutil.rmtree(INSTALLED_DIRS[top], ignore_errors=True)
    if mods_present and MODS_DIR.exists():
        for old in MODS_DIR.glob("*.zip"):
            try:
                old.unlink()
            except OSError as e:
                log.warning(f"Could not remove old mod {old.name}: {e}")
    if state_present:
        present = {dest.name for _member, dest in entries
                   if dest.parent == STATE_DIR}
        for name in STATE_FILES:
            if name not in present:
                try:
                    (STATE_DIR / name).unlink()
                except FileNotFoundError:
                    pass
                except OSError as e:
                    log.warning(f"Could not remove old state {name}: {e}")

    restored = []
    with zipfile.ZipFile(backup_path, "r") as zf:
        for member, dest in entries:
            _extract(zf, member, dest)
            restored.append(member)

    return restored


def reset_all():
    removed = []
    overlay_removed = False
    for name in paths.OVERLAY_ROOTS:
        top = OVERLAY_DIR / name
        if top.exists():
            try:
                shutil.rmtree(top)
                overlay_removed = True
            except OSError as e:
                log.warning(f"Could not remove {top}: {e}")
    if overlay_removed:
        removed.append("overlay")

    for name, src in INSTALLED_DIRS.items():
        if src.exists():
            try:
                shutil.rmtree(src)
                removed.append(name)
            except OSError as e:
                log.warning(f"Could not remove {src}: {e}")

    if LUTION_CONFIG.exists():
        data, comments = fflags.load_config()
        data["fflags"] = {}
        try:
            fflags.save_config(data, comments)
            removed.append("config")
        except OSError as e:
            log.warning(f"Could not reset config: {e}")

    manifest = STATE_DIR / "mods_manifest.json"
    if manifest.exists():
        try:
            manifest.unlink()
            removed.append("mods manifest")
        except OSError as e:
            log.warning(f"Could not clear mods manifest: {e}")

    for name in ("theme.json", "env_vars.json", "launcher_config.json",
                 "fflag_user_presets.json", "marketplace_installed.json"):
        path = STATE_DIR / name
        if path.exists():
            try:
                path.unlink()
                removed.append(name)
            except OSError as e:
                log.warning(f"Could not remove {name}: {e}")

    paths.ensure_lution_dirs()
    return removed
