# basically managing sober like reinstalling uninstalling installing updating
import subprocess
from pathlib import Path

import log

SOBER_APP_ID = "org.vinegarhq.Sober"
REMOTE = "flathub"
FLATHUB_REPO = "https://flathub.org/repo/flathub.flatpakrepo"
SOBER_DATA_DIR = Path.home() / ".var/app" / SOBER_APP_ID

def _run(cmd, timeout=15):
    try:
        return subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout)
    except subprocess.TimeoutExpired:
        log.warning(f"Command timed out after {timeout}s: {cmd[0]} {cmd[1] if len(cmd)>1 else ''}")
        return None

def _stream(args, output_cb=None):
    try:
        proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
    except FileNotFoundError:
        return False, "flatpak not found on this system"

    def emit(raw):
        line = raw.decode(errors="replace").strip()
        if line and output_cb:
            output_cb(line)

    buf = b""
    while True:
        chunk = proc.stdout.read(1)
        if not chunk:
            break
        if chunk in (b"\n", b"\r"):
            emit(buf)
            buf = b""
        else:
            buf += chunk
    emit(buf)
    proc.wait()

    ok = proc.returncode == 0
    return ok, "done" if ok else "failed"

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
    result = _run(["flatpak", "remote-add", "--if-not-exists", REMOTE,
                    FLATHUB_REPO])
    if result is None:
        return False, "flatpak command timed out"
    return result.returncode == 0, (result.stderr or "").strip()

def get_version():
    result = _run(["flatpak", "info", SOBER_APP_ID])
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
    result = _run(["flatpak", "info", SOBER_APP_ID])
    if result is None or result.returncode != 0:
        return ""
    return _commit_from_output(result.stdout)

def remote_commit():
    result = _run(["flatpak", "remote-info", REMOTE, SOBER_APP_ID])
    if result is None or result.returncode != 0:
        return ""
    return _commit_from_output(result.stdout)

def remote_commit():
    result = _run(["flatpak", "remote-info", REMOTE, SOBER_APP_ID])
    if result.returncode != 0:
        return ""
    return _commit_from_output(result.stdout)

def install(output_cb=None):
    return _stream(["flatpak", "install", "-y", REMOTE, SOBER_APP_ID], output_cb)

def update(output_cb=None):
    return _stream(["flatpak", "update", "-y", SOBER_APP_ID], output_cb)

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
    if not remote:
        log.warning("Flathub unreachable, skipping update check")
        if output_cb:
            output_cb("Can't reach Flathub — launching installed Sober")
        return True, "offline"

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
    return _stream(["flatpak", "uninstall", "-y", SOBER_APP_ID], output_cb)

def delete_sober_data():
    import shutil
    if SOBER_DATA_DIR.exists():
        shutil.rmtree(SOBER_DATA_DIR, ignore_errors=True)
        return not SOBER_DATA_DIR.exists()
    return True
