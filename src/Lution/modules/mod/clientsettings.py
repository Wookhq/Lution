import os
import json
from modules.json.json import UpdateSoberConfig, ReadSoberConfig
from pathlib import Path

def CheckClientSettings(config_fl):
    client_app_settings_path = os.path.join(os.path.expanduser(config_fl), "ClientAppSettings.json")
    dump = os.path.expanduser("~/Documents/Lution/fflag dump")
    dump_file_path = os.path.join(dump, "ClientAppSettings.json")
    
    Path(dump).mkdir(parents=True, exist_ok=True)
    with open(client_app_settings_path, "r") as r:
        content = r.read()
        with open(dump_file_path, "w") as f:
            try:
                f.write(content)  # dump raw text into file

                # parse to dict (from the stringified JSON inside content)
                parsed = json.loads(content)

                # store as dict not a string
                UpdateSoberConfig("fflags", parsed)

            except Exception as e:
                print(f"Error writing to {dump}: {e}")
                return

def ClientSettingsContent():
    dump = os.path.expanduser("~/Documents/Lution/fflag dump/ClientAppSettings.json")
    try:
        with open(dump, "r") as f:
            content = json.load(f)
        return content if content else {}
    except Exception as e:
        print(f"Error reading {dump}: {e}")
        return {}

def SplitClientSettingsContent():
    dumped = ClientSettingsContent()
    currfflag = ReadSoberConfig("fflags")

    if not isinstance(currfflag, dict):
        currfflag = {}

    if not isinstance(dumped, dict):
        dumped = {}

    keys_to_delete = [k for k, v in currfflag.items() if k in dumped and dumped[k] == v]
    for k in keys_to_delete:
        del currfflag[k]

    final = json.dumps(currfflag, indent=4)
    return final