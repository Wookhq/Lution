# basically managing sober like reinstalling uninstalling installing updating
# this is now useless because it's replaced with a how to install sober etc etc button
import subprocess
from pathlib import Path
import os
import select
import time

import log

SOBER_APP_ID = "org.vinegarhq.Sober"
REMOTE = "flathub"
FLATHUB_REPO = "https://flathub.org/repo/flathub.flatpakrepo"
SOBER_DATA_DIR = Path.home() / ".var/app" / SOBER_APP_ID

REMOTE_TIMEOUT = 45
STREAM_TIMEOUT = 30 * 60


def clean_env(env=None):
    env = dict(os.environ if env is None else env)
    for key in ("LD_PRELOAD", "LD_LIBRARY_PATH",
                "PYTHONHOME", "PYTHONPATH", "PYTHONSTARTUP",
                "PYTHONUSERBASE", "PYTHONNOUSERSITE", "PYTHONEXECUTABLE",
                "GI_TYPELIB_PATH", "GSETTINGS_SCHEMA_DIR",
                "GDK_PIXBUF_MODULE_FILE", "GDK_PIXBUF_MODULEDIR",
                "GTK_PATH", "GTK_DATA_PREFIX", "GTK_EXE_PREFIX",
                "GTK_IM_MODULE_FILE", "APPDIR"):
        env.pop(key, None)
    for key in list(env):
        if key.startswith(("_MEI", "_PYI", "NUITKA_")):
            env.pop(key, None)
    return env


def _run(cmd, timeout=15):
    try:
        return subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout, env=clean_env())
    except subprocess.TimeoutExpired:
        log.warning(f"Command timed out after {timeout}s: {cmd[0]} {cmd[1] if len(cmd)>1 else ''}")
        return None
    except OSError as e:
        log.warning(f"Could not run {cmd[0]}: {e}")
        return None
def _stream(args, output_cb=None, timeout=STREAM_TIMEOUT):
    try:
        proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, env=clean_env())
    except FileNotFoundError:
        return False, "flatpak not found on this system"

    def emit(raw):
        line = raw.decode(errors="replace").strip()
        if line and output_cb:
            output_cb(line)

    deadline = time.monotonic() + timeout
    buf = b""
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            proc.kill()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
            log.error(f"Command timed out after {timeout}s: {' '.join(args)}")
            return False, f"timed out after {timeout}s"
        try:
            ready, _, _ = select.select([proc.stdout], [], [], remaining)
        except (OSError, ValueError):
            break
        if not ready:
            continue
        chunk = proc.stdout.read(1)
        if not chunk:
            break
        if chunk in (b"\n", b"\r"):
            emit(buf)
            buf = b""
        else:
            buf += chunk
    emit(buf)

    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        log.error(f"Command timed out while finishing: {' '.join(args)}")
        return False, "timed out"

    ok = proc.returncode == 0
    return ok, "done" if ok else "failed"

def _installed_flag():
    result = _run(["flatpak", "list", "--app",
                   "--columns=application,installation"])
    if result is None or result.returncode != 0:
        return None
    for line in result.stdout.splitlines():
        parts = [p.strip() for p in line.split("\t")]
        if len(parts) >= 2 and parts[0] == SOBER_APP_ID:
            if parts[1] in ("user", "system"):
                return "--" + parts[1]
    return None


def installed_flag():
    return _installed_flag()


def _remote_flag():
    for flag in ("--system", "--user"):
        result = _run(["flatpak", "remotes", flag, "--columns=name"])
        if result is None or result.returncode != 0:
            continue
        for line in result.stdout.splitlines():
            if line.strip() == REMOTE:
                return flag
    return "--system"


def is_installed():
    result = _run(["flatpak", "list", "--app", "--columns=application"])
    if result is None or result.returncode != 0:
        return False
    for line in result.stdout.splitlines():
        if line.strip() == SOBER_APP_ID:
            return True
    return False

def has_flathub():
    result = _run(["flatpak", "remotes", "--columns=name"])
    if result is None or result.returncode != 0:
        return False
    for line in result.stdout.splitlines():
        if line.strip() == REMOTE:
            return True
    return False

def add_flathub():
    result = _run(["flatpak", "remote-add", "--if-not-exists", "--system",
                    REMOTE, FLATHUB_REPO])
    if result is None:
        return False, "flatpak command timed out"
    return result.returncode == 0, (result.stderr or "").strip()

def get_version():
    flag = _installed_flag()
    result = _run(["flatpak", "info"] + ([flag] if flag else [])
                  + [SOBER_APP_ID])
    if result is None or result.returncode != 0:
        return ""
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if stripped.startswith("Version:"):
            return stripped.split(":", 1)[1].strip()
    return ""

def _commit_from_output(text):
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("Commit:"):
            return stripped.split(":", 1)[1].strip()
    return ""

def installed_commit():
    flag = _installed_flag()
    result = _run(["flatpak", "info"] + ([flag] if flag else [])
                  + [SOBER_APP_ID])
    if result is None or result.returncode != 0:
        return ""
    return _commit_from_output(result.stdout)

def remote_commit():
    flag = _installed_flag() or _remote_flag()
    result = _run(["flatpak", "remote-info", flag, REMOTE, SOBER_APP_ID],
                  timeout=REMOTE_TIMEOUT)
    if result is None or result.returncode != 0:
        return None
    return _commit_from_output(result.stdout)

def install(output_cb=None):
    return _stream(["flatpak", "install", "-y", _remote_flag(), REMOTE,
                    SOBER_APP_ID], output_cb)

def update(output_cb=None):
    flag = _installed_flag() or _remote_flag()
    return _stream(["flatpak", "update", "-y", flag, SOBER_APP_ID], output_cb)

def ensure_sober(output_cb=None):
    if not is_installed():
        log.info("Sober not found, installing")
        if output_cb:
            output_cb("Sober not found, installing...")
        if not has_flathub():
            log.info("Adding flathub remote")
            if output_cb:
                output_cb("Adding flathub remote...")
            ok, err = add_flathub()
            if not ok:
                log.error(f"Could not add flathub: {err}")
                return False, f"Could not add flathub how weird: {err}"
        return install(output_cb)

    remote = remote_commit()
    if remote is None:
        log.error("Could not reach Flathub to check for Sober updates")
        if output_cb:
            output_cb("Could not reach Flathub")
        return False, "could not reach Flathub to check for updates"
    if not remote:
        log.error("Flathub did not report Sober's latest commit")
        if output_cb:
            output_cb("Flathub did not report Sober's latest version")
        return False, "Flathub did not report Sober's latest version"

    local = installed_commit()
    if local and local == remote:
        log.info(f"Sober is already up to date (v{get_version()})")
        if output_cb:
            output_cb("Sober is already up to date")
        return True, "already up to date"

    log.info("Sober found, checking for updates")
    if output_cb:
        output_cb("Sober found, checking for updates...")
    return update(output_cb)

def uninstall(output_cb=None):
    flag = _installed_flag() or _remote_flag()
    return _stream(["flatpak", "uninstall", "-y", flag, SOBER_APP_ID], output_cb)

def delete_sober_data():
    import shutil
    if SOBER_DATA_DIR.exists():
        shutil.rmtree(SOBER_DATA_DIR, ignore_errors=True)
        return not SOBER_DATA_DIR.exists()
    return True
