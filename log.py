# logging yeahh

import sys
from datetime import datetime
from pathlib import Path

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

LOG_FILE = Path.home() / ".local/Lution/lution.log"


def _log(level, msg):
    color = LEVEL_COLORS.get(level, WHITE)
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    stream = sys.stderr if level == "error" else sys.stdout
    print(f"{time_str} {BLUE}lution{RESET} {color}{level}{RESET} {msg}",
          file=stream, flush=True)
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        stamp = now.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as f:
            f.write(f"{stamp} lution {level} {msg}\n")
    except OSError:
        pass


def info(msg):
    _log("info", msg)


def debug(msg):
    _log("debug", msg)


def warning(msg):
    _log("warning", msg)


def error(msg):
    _log("error", msg)
