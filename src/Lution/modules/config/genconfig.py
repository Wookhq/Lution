import json
import os
import toml
from modules.utils.logging import log

log = log()

class Config:
    def __init__(self, config_filename="LutionConfig.toml"):
        from modules.utils.files import FilesFunctions
        self.ff = FilesFunctions()
        self.config_dir = os.path.expanduser("~/Documents/Lution")
        self.config_path = os.path.join(self.config_dir, config_filename)
        self.ff.JsonSetup()

    def _read_data(self):
        if not os.path.exists(self.config_path):
            return {}
        with open(self.config_path, "r") as f:
            try:
                return toml.load(f)
            except toml.TomlDecodeError:
                log.error(f"Failed to decode TOML config at '{self.config_path}'. It might be corrupted.")
                return {}

    def _write_data(self, data):
        with open(self.config_path, "w") as f:
            toml.dump(data, f)

    def Read(self, section, key, default=None):
        data = self._read_data()
        return data.get(section, {}).get(key, default)

    def Update(self, section, key, value):
        data = self._read_data()
        if section not in data:
            data[section] = {}
        data[section][key] = value
        self._write_data(data)
        log.info(f"Config [{section}]['{key}'] set to {value}")

    def RemoveValueFromList(self, section, key, value_to_remove):
        data = self._read_data()
        if section in data and key in data[section]:
            current_value = data[section][key]
            if not isinstance(current_value, str):
                log.warn(f"Cannot remove value from non-string key '{key}' in section '{section}'.")
                return
            values = [v.strip() for v in current_value.split(',')]
            if value_to_remove in values:
                values.remove(value_to_remove)
                data[section][key] = ','.join(values)
                self._write_data(data)
                log.info(f"Removed '{value_to_remove}' from [{section}]['{key}'].")
            else:
                log.warn(f"Value '{value_to_remove}' not found in key '{key}'.")
        else:
            log.warn(f"Key '{key}' not found in section '{section}'.")

    def ConvertOldConfigs(self):
        log.info("Checking for old configuration files to convert...")

        old_marketplace_config_path = os.path.expanduser("~/Documents/Lution/Lution Marketplace/Marketplace.toml")

        current_data = self._read_data()
        config_was_updated = False

        if os.path.exists(old_marketplace_config_path):
            log.info(f"Found old marketplace config: {old_marketplace_config_path}")
            with open(old_marketplace_config_path, "r") as f:
                marketplace_data = toml.load(f)

            if 'marketplace' not in current_data:
                current_data['marketplace'] = {}
            current_data['marketplace'].update(marketplace_data)

            os.remove(old_marketplace_config_path)
            log.info(f"Removed old file: {old_marketplace_config_path}")
            try:
                os.rmdir(os.path.dirname(old_marketplace_config_path))
                log.info("Removed old marketplace directory as it is now empty.")
            except OSError:
                log.warn("Old marketplace directory is not empty, so it was not removed.")

            config_was_updated = True

        lution_items = {}
        other_sections = {}
        for key, value in current_data.items():
            if not isinstance(value, dict):
                lution_items[key] = value
            else:
                other_sections[key] = value

        if lution_items:
            log.info("Found top-level settings. Moving them to [lution] section.")
            if 'lution' not in other_sections:
                other_sections['lution'] = {}
            other_sections['lution'].update(lution_items)
            current_data = other_sections
            config_was_updated = True

        if config_was_updated:
            self._write_data(current_data)
            log.info("Configuration file was updated to the new format.")
        else:
            log.info("No old configuration files found or no conversion needed.")

    def ReadSoberConfig(self, key):
        file_path = os.path.expanduser("~/.var/app/org.vinegarhq.Sober/config/sober/config.json")
        try:
            with open(file_path, "r") as f:
                config = json.load(f)
            return config.get(key, None)
        except Exception as e:
            log.error(f"Failed to read setting '{key}': {e}")
            return None

    def ReadFflagsConfig(self, flag_name):
        file_path = os.path.expanduser("~/.var/app/org.vinegarhq.Sober/config/sober/config.json")
        try:
            with open(file_path, "r") as f:
                config = json.load(f)
            return config.get("fflags", {}).get(flag_name, None)
        except Exception as e:
            log.error(f"Failed to read fflag '{flag_name}': {e}")
            return None

    def DeleteFflag(self, flag_name):
        file_path = os.path.expanduser("~/.var/app/org.vinegarhq.Sober/config/sober/config.json")
        try:
            with open(file_path, "r") as f:
                config = json.load(f)
            fflags = config.get("fflags", {})
            if flag_name in fflags:
                del fflags[flag_name]
                config["fflags"] = fflags
                with open(file_path, "w") as f:
                    json.dump(config, f, indent=4)
                return True
            else:
                log.warn(f"Flag '{flag_name}' not found in fflags.")
                return False
        except Exception as e:
            log.error(f"Failed to delete fflag '{flag_name}': {e}")
            return False

    def UpdateFflags(self, flag_name, flag_value):
        file_path = os.path.expanduser("~/.var/app/org.vinegarhq.Sober/config/sober/config.json")
        try:
            with open(file_path, "r") as f:
                sober_config = json.load(f)
            if "fflags" not in sober_config or not isinstance(sober_config["fflags"], dict):
                sober_config["fflags"] = {}
            sober_config["fflags"][flag_name] = flag_value
            with open(file_path, "w") as f:
                json.dump(sober_config, f, indent=4)
            log.info(f"fflags['{flag_name}'] set to {flag_value}")
        except Exception as e:
            log.error(f"Failed to update fflags: {e}")

    def UpdateSoberConfig(self, key, value):
        file_path = os.path.expanduser("~/.var/app/org.vinegarhq.Sober/config/sober/config.json")
        try:
            with open(file_path, "r") as f:
                config = json.load(f)
            config[key] = value
            with open(file_path, "w") as f:
                json.dump(config, f, indent=4)
            log.info(f"Config['{key}'] set to {value}")
        except Exception as e:
            log.error(f"Failed to update config: {e}")

    def CombineJson(self, *json_objs):
        result = {}
        for obj in json_objs:
            if isinstance(obj, dict):
                result.update(obj)
            else:
                log.warn(f"Skipped non-dict object in CombineJson: {type(obj)}")
        return result

    @staticmethod
    def Json2Toml(json_path, toml_path=None):
        if not os.path.isfile(json_path):
            raise FileNotFoundError(f"ermmm where tf is the json file: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        if toml_path is None:
            toml_path = os.path.splitext(json_path)[0] + ".toml"

        with open(toml_path, "w", encoding="utf-8") as f:
            toml.dump(json_data, f)
