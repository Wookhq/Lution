# backup for both sober and lution so you can get the exact same setup fast
from pathlib import Path
import json
import shutil
import tempfile
import zipfile

import paths
import log
import fflags
import sync

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


def _replace(staged, final, old_root, swaps):
    final = Path(final)
    backup = old_root / str(len(swaps))
    if final.exists() or final.is_symlink():
        shutil.move(str(final), str(backup))
    if staged is not None:
        staged = Path(staged)
        final.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(staged), str(final))
    swaps.append((staged, final, backup))


def _rollback(swaps):
    for staged, final, backup in reversed(swaps):
        try:
            if final.is_dir() and not final.is_symlink():
                shutil.rmtree(final)
            elif final.exists() or final.is_symlink():
                final.unlink()
        except OSError as e:
            log.warning(f"Could not remove restored path {final}: {e}")
        try:
            if backup.exists() or backup.is_symlink():
                final.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(backup), str(final))
        except OSError as e:
            log.error(f"Could not restore backup {backup} to {final}: {e}")
    swaps.clear()


@sync.locked
def import_backup(backup_path):
    backup_path = Path(backup_path)
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup not found: {backup_path}")

    entries = []
    overlay_roots = set()
    installed_roots = set()
    state_names = set()
    mods_present = False
    config_present = False

    with zipfile.ZipFile(backup_path, "r") as zf:
        for member in zf.namelist():
            if member.endswith("/"):
                continue

            if member == "config.json":
                try:
                    raw = zf.read(member).decode("utf-8")
                    _comments, body = fflags._split_comments(raw)
                    data = json.loads(body) if body.strip() else None
                except (UnicodeError, ValueError) as e:
                    raise ValueError(f"Backup config.json is invalid: {e}") from e
                if not isinstance(data, dict):
                    raise ValueError("Backup config.json is not a JSON object")
                entries.append((member, "config.json"))
                config_present = True
                continue

            if member.startswith("asset_overlay/"):
                rest = member[len("asset_overlay/"):]
                top = rest.split("/", 1)[0]
                if top not in paths.OVERLAY_ROOTS:
                    log.warning(f"Skipping unknown overlay entry: {member}")
                    continue
                try:
                    _safe_dest(OVERLAY_DIR, rest)
                except ValueError as e:
                    log.error(f"Skipping unsafe backup entry: {e}")
                    continue
                entries.append((member, "asset_overlay/" + rest))
                overlay_roots.add(top)
                continue

            if member.startswith("installed/"):
                rest = member[len("installed/"):]
                top = rest.split("/", 1)[0]
                if top not in INSTALLED_DIRS:
                    log.warning(f"Skipping unknown installed entry: {member}")
                    continue
                try:
                    _safe_dest(paths.LUTION_ROOT, rest)
                except ValueError as e:
                    log.error(f"Skipping unsafe backup entry: {e}")
                    continue
                entries.append((member, "installed/" + rest))
                installed_roots.add(top)
                continue

            if member.startswith("lution/"):
                rest = member[len("lution/"):]
                if rest not in STATE_FILES:
                    log.warning(f"Skipping non-backup state entry: {member}")
                    continue
                entries.append((member, "lution/" + rest))
                state_names.add(rest)
                continue

            if member.startswith("mods/"):
                rest = member[len("mods/"):]
                if "/" in rest or not rest.endswith(".zip"):
                    log.warning(f"Skipping unknown mod entry: {member}")
                    continue
                try:
                    _safe_dest(MODS_DIR, rest)
                except ValueError as e:
                    log.error(f"Skipping unsafe backup entry: {e}")
                    continue
                entries.append((member, "mods/" + rest))
                mods_present = True
                continue

            log.warning(f"Skipping unknown backup entry: {member}")

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="lution_backup_", dir=str(STATE_DIR)))
    swaps = []
    try:
        with zipfile.ZipFile(backup_path, "r") as zf:
            for member, rel in entries:
                dest = _safe_dest(stage, rel)
                dest.parent.mkdir(parents=True, exist_ok=True)
                _extract(zf, member, dest)

        if config_present:
            _comments, body = fflags._split_comments(
                (stage / "config.json").read_text())
            if not isinstance(json.loads(body) if body.strip() else None, dict):
                raise ValueError("Backup config.json is not a JSON object")

        for name in state_names:
            try:
                data = json.loads((stage / "lution" / name).read_text())
            except (UnicodeError, ValueError) as e:
                raise ValueError(f"Backup state file {name} is invalid: {e}") from e
            if name == "mods_manifest.json" and not isinstance(data, list):
                raise ValueError("Backup mods manifest is invalid")
            if name != "mods_manifest.json" and not isinstance(data, dict):
                raise ValueError(f"Backup state file {name} is invalid")

        if mods_present:
            for fp in (stage / "mods").glob("*.zip"):
                try:
                    with zipfile.ZipFile(fp, "r") as zf:
                        if zf.testzip() is not None:
                            raise ValueError(f"Backup mod {fp.name} is corrupt")
                except zipfile.BadZipFile as e:
                    raise ValueError(
                        f"Backup mod {fp.name} is not a ZIP archive") from e

        old_root = stage / "old"
        old_root.mkdir()

        for top in sorted(overlay_roots):
            staged = stage / "asset_overlay" / top
            if staged.exists():
                _replace(staged, OVERLAY_DIR / top, old_root, swaps)
        for top in sorted(installed_roots):
            staged = stage / "installed" / top
            if staged.exists():
                _replace(staged, INSTALLED_DIRS[top], old_root, swaps)
        if config_present:
            _replace(stage / "config.json", LUTION_CONFIG, old_root, swaps)
        if state_names:
            for name in STATE_FILES:
                staged = stage / "lution" / name
                if staged.exists():
                    _replace(staged, STATE_DIR / name, old_root, swaps)
                else:
                    _replace(None, STATE_DIR / name, old_root, swaps)
        if mods_present:
            for old in MODS_DIR.glob("*.zip"):
                _replace(None, old, old_root, swaps)
            for staged in (stage / "mods").glob("*.zip"):
                _replace(staged, MODS_DIR / staged.name, old_root, swaps)

        shutil.rmtree(stage, ignore_errors=True)
        return [member for member, _rel in entries]
    except BaseException:
        _rollback(swaps)
        log.error(f"Backup import failed; staged files kept at {stage}")
        raise


@sync.locked
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
