import os
import json
from modules.config.genconfig import Config
from pathlib import Path

_config_instance = None


def get_config():
    global _config_instance
    if _config_instance is None:
        from modules.config.genconfig import Config

        _config_instance = Config()
    return _config_instance


class ClientSettings:
    def __init__(self):
        pass

    def CheckClientSettings(self, config_fl):
        client_app_settings_path = os.path.join(
            os.path.expanduser(config_fl), "ClientAppSettings.json"
        )
        dump = os.path.expanduser("~/Documents/Lution/fflag dump")
        dump_file_path = os.path.join(dump, "ClientAppSettings.json")

        Path(dump).mkdir(parents=True, exist_ok=True)
        if os.path.exists(client_app_settings_path):
            with open(client_app_settings_path, "r") as r:
                content = r.read()
                with open(dump_file_path, "w") as f:
                    try:
                        f.write(content)
                        parsed = json.loads(content)
                        get_config().UpdateSoberConfig("fflags", parsed)

                    except Exception as e:
                        print(f"Error writing to {dump}: {e}")
                        return
        else:
            return

    def ClientSettingsContent(self):
        dump = os.path.expanduser(
            "~/Documents/Lution/fflag dump/ClientAppSettings.json"
        )
        try:
            with open(dump, "r") as f:
                content = json.load(f)
            return content if content else {}
        except Exception as e:
            print(f"Error reading {dump}: {e}")
            return {}

    def SplitClientSettingsContent(self):
        dumped = self.ClientSettingsContent()
        currfflag = get_config().ReadSoberConfig("fflags")

        if not isinstance(currfflag, dict):
            currfflag = {}

        if not isinstance(dumped, dict):
            dumped = {}

        keys_to_delete = [
            k for k, v in currfflag.items() if k in dumped and dumped[k] == v
        ]
        for k in keys_to_delete:
            del currfflag[k]

        final = json.dumps(currfflag, indent=4)
        return final
