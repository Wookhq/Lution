# builds the command that actually starts sober

import os
import shutil
import subprocess
from pathlib import Path

import paths
import envvars
import log

_BWRAP_FALLBACKS = (
    "/usr/bin/bwrap",
    "/bin/bwrap",
    "/usr/local/bin/bwrap",
    "/usr/libexec/bwrap",
    "/usr/libexec/flatpak-bwrap",
    "/usr/lib/flatpak/bwrap",
)


def find_bwrap():
    override = os.environ.get("FLATPAK_BWRAP")
    if override and os.access(override, os.X_OK):
        return override

    found = shutil.which("bwrap")
    if found:
        return found

    flatpak = shutil.which("flatpak")
    if flatpak:
        sibling = Path(flatpak).parent / "bwrap"
        if sibling.is_file() and os.access(sibling, os.X_OK):
            return str(sibling)

    for path in _BWRAP_FALLBACKS:
        if os.access(path, os.X_OK):
            return path

    return None


class LaunchError(Exception):
    pass


BWRAP = find_bwrap()


def userns_available():
    if not BWRAP:
        return False
    try:
        result = subprocess.run(
            [BWRAP, "--bind", "/", "/", "--dev-bind", "/dev", "/dev",
             "--proc", "/proc", "--", "true"],
            capture_output=True, timeout=10,
        )
        return result.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def sober_is_running():
    try:
        result = subprocess.run(["flatpak", "ps"], capture_output=True,
                                text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return False
    return paths.SOBER_APP_ID in result.stdout


def seed_config():
    if paths.LUTION_CONFIG.exists():
        return
    paths.LUTION_ROOT.mkdir(parents=True, exist_ok=True)
    if paths.SOBER_CONFIG.exists():
        shutil.copyfile(paths.SOBER_CONFIG, paths.LUTION_CONFIG)
        log.info("Seeded lution config from sober's config.json")
    else:
        paths.LUTION_CONFIG.write_text('{\n    "fflags": {}\n}\n')
        log.info("Sober has no config.json yet, starting a fresh one")


def _overlay_args():
    args = []
    for name in paths.OVERLAY_ROOTS:
        lution_dir = paths.LUTION_OVERLAY / name
        lution_dir.mkdir(parents=True, exist_ok=True)
        args += ["--bind", str(lution_dir), str(paths.SOBER_OVERLAY / name)]
    return args


def build_sober_command(url=None):
    if not BWRAP:
        raise LaunchError(
            "Could not find bubblewrap (bwrap). Flatpak depends on it, so this "
            "usually means the Flatpak install is incomplete - try reinstalling "
            "flatpak, or install the bubblewrap package."
        )
    if not userns_available():
        raise LaunchError(
            "Bubblewrap could not create a mount namespace here. Flatpak needs "
            "the same capability, so Sober itself would not start either - "
            "check that your kernel allows user namespaces."
        )
    if sober_is_running():
        raise LaunchError(
            "Sober is already running. Close it first, otherwise it keeps the "
            "files it was started with."
        )

    paths.migrate_legacy_overlay()
    seed_config()

    args = [BWRAP,
            "--bind", "/", "/",
            "--dev-bind", "/dev", "/dev",
            "--proc", "/proc",
            "--chdir", "/"]
    args += _overlay_args()

    if paths.SOBER_CONFIG.exists():
        args += ["--bind", str(paths.LUTION_CONFIG), str(paths.SOBER_CONFIG)]

    args += ["--", "flatpak", "run"]
    args += envvars.env_flatpak_args()
    args += [paths.SOBER_APP_ID]
    if url:
        args.append(url)
    return args


def launch(url=None, stdout=None, stderr=None, env=None):
    args = build_sober_command(url)
    log.info("Launching Sober with lution overlay")
    return subprocess.Popen(args, stdout=stdout, stderr=stderr, env=env)


def launch_plain(url=None):
    args = ["flatpak", "run"]
    args += envvars.env_flatpak_args()
    args += [paths.SOBER_APP_ID]
    if url:
        args.append(url)
    log.info("launching normal sober")
    return subprocess.Popen(args)
