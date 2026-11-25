import os
import sys
import tempfile
import threading
import traceback
from datetime import datetime
from pathlib import Path

import paths

RESET = "\x1b[0m"
BLUE = "\x1b[34m"
WHITE = "\x1b[37m"
RED = "\x1b[31m"
YELLOW = "\x1b[33m"

LEVEL_COLORS = {
    "info": WHITE,
    "debug": WHITE,
    "warning": YELLOW,
    "error": RED,
}

_SESSION_STAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
LOG_DIR = paths.STATE_DIR / "logs"
LOG_FILE = LOG_DIR / f"{_SESSION_STAMP}_{os.getpid()}.log"
FALLBACK_FILE = (Path(tempfile.gettempdir())
                 / f"lution-{os.getuid()}_{_SESSION_STAMP}_{os.getpid()}.log")

_active_file = LOG_FILE
_fallback_reported = False


def _append(path, line):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "a") as stream:
        stream.write(line)


def _write_file(line, now):
    global _active_file, _fallback_reported
    try:
        _append(_active_file, line)
        return
    except OSError as e:
        if _active_file != LOG_FILE:
            print(f"{now.strftime('%H:%M:%S')} lution warning could not write "
                  f"{_active_file}: {e}", file=sys.stderr, flush=True)
            return
        if not _fallback_reported:
            _fallback_reported = True
            print(f"{now.strftime('%H:%M:%S')} lution warning could not write "
                  f"{LOG_FILE}: {e}; falling back to {FALLBACK_FILE}",
                  file=sys.stderr, flush=True)
        _active_file = FALLBACK_FILE
        try:
            _append(_active_file, line)
        except OSError as e2:
            print(f"{now.strftime('%H:%M:%S')} lution error could not write "
                  f"{_active_file}: {e2}", file=sys.stderr, flush=True)


def _log(level, msg):
    color = LEVEL_COLORS.get(level, WHITE)
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    if level != "debug":
        stream = sys.stderr if level == "error" else sys.stdout
        try:
            print(f"{time_str} {BLUE}lution{RESET} {color}{level}{RESET} {msg}",
                  file=stream, flush=True)
        except OSError:
            pass
    stamp = now.strftime("%Y-%m-%d %H:%M:%S")
    _write_file(f"{stamp} lution {level} {msg}\n", now)


def _format(exc_type, exc_value, exc_tb):
    return "".join(
        traceback.format_exception(exc_type, exc_value, exc_tb)).rstrip()


def info(msg):
    _log("info", msg)


def debug(msg):
    _log("debug", msg)


def warning(msg):
    _log("warning", msg)


def error(msg):
    _log("error", msg)


def exception(msg):
    _log("error", f"{msg}\n{traceback.format_exc().rstrip()}")


def tk_exception(exc_type, exc_value, exc_tb):
    _log("error", "unhandled Tk callback exception\n"
         + _format(exc_type, exc_value, exc_tb))


def install_hooks():
    def handle_exception(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        _log("error", "uncaught exception\n"
             + _format(exc_type, exc_value, exc_tb))

    sys.excepthook = handle_exception

    def handle_thread(args):
        name = args.thread.name if args.thread is not None else "unknown"
        _log("error", f"uncaught exception in thread {name}\n"
             + _format(args.exc_type, args.exc_value, args.exc_traceback))

    threading.excepthook = handle_thread
