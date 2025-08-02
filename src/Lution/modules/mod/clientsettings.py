import os
from modules.json.json import UpdateFflags
from pathlib import Path

def CheckClientSettings(config_fl):
    client_app_settings_path = os.path.join(os.path.expanduser(config_fl), "ClientAppSettings.json")
    dump = os.path.expanduser("~/Documents/Lution/Mods/fflag dump")
    dump_file_path = os.path.join(dump, "ClientAppSettings.json")
    
    Path(dump).mkdir(parents=True, exist_ok=True)
    with open(client_app_settings_path, "r") as r:
        content = r.read()
        with open(dump_file_path, "w") as f:
            try :
                f.write(content)
                UpdateFflags(content)
            except Exception as e:
                print(f"Error writing to {dump}: {e}")
                return