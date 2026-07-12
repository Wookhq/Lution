# self explanatory

import subprocess
import sys

SOBER_APP_ID = "org.vinegarhq.Sober"

args = ["flatpak", "run", SOBER_APP_ID]
if len(sys.argv) > 1:
    args.append(sys.argv[1])

subprocess.Popen(args)
