import os
import json
from modules.config.genconfig import Config
from pathlib import Path

cg = Config()

class ClientSettings:
    def __init__(self):
        pass


    def CheckClientSettings(self, config_fl):
        client_app_settings_path = os.path.join(os.path.expanduser(config_fl), "ClientAppSettings.json")
        dump = os.path.expanduser("~/Documents/Lution/fflag dump")
        dump_file_path = os.path.join(dump, "ClientAppSettings.json")
        
        Path(dump).mkdir(parents=True, exist_ok=True)
        with open(client_app_settings_path, "r") as r:
            content = r.read()
            with open(dump_file_path, "w") as f:
                try:
                    f.write(content)  
                    parsed = json.loads(content)
                    cg.UpdateSoberConfig("fflags", parsed)

                except Exception as e:
                    print(f"Error writing to {dump}: {e}")
                    return

    def ClientSettingsContent(self):
        dump = os.path.expanduser("~/Documents/Lution/fflag dump/ClientAppSettings.json")
        try:
            with open(dump, "r") as f:
                content = json.load(f)
            return content if content else {}
        except Exception as e:
            print(f"Error reading {dump}: {e}")
            return {}

    def SplitClientSettingsContent(self):
        dumped = self.ClientSettingsContent()
        currfflag = cg.ReadSoberConfig("fflags")

        if not isinstance(currfflag, dict):
            currfflag = {}

        if not isinstance(dumped, dict):
            dumped = {}

        keys_to_delete = [k for k, v in currfflag.items() if k in dumped and dumped[k] == v]
        for k in keys_to_delete:
            del currfflag[k]

        final = json.dumps(currfflag, indent=4)
        return final