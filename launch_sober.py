# self explanatory

import json
import subprocess
import sys
from pathlib import Path

SOBER_APP_ID = "org.vinegarhq.Sober"
ENV_FILE = Path.home() / ".local/Lution/env_vars.json"

args = ["flatpak", "run"]

try:
    env_vars = json.loads(ENV_FILE.read_text())
    if isinstance(env_vars, dict):
        for key, value in env_vars.items():
            args.append(f"--env={key}={value}")
except Exception:
    pass

args.append(SOBER_APP_ID)

if len(sys.argv) > 1:
    args.append(sys.argv[1])

subprocess.Popen(args)
