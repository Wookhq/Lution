#src/Lution/modules/json/json.py
import json
import os
import toml
from modules.utils.messages import STMessages\

st = STMessages()

class Config:
    def __init__(self):
        pass    
    
    def ReadSoberConfig(self, key):
        """Read a top-level value from the Sober config (outside fflags)."""
        file_path = os.path.expanduser("~/.var/app/org.vinegarhq.Sober/config/sober/config.json")
        try:
            with open(file_path, "r") as f:
                config = json.load(f)
            return config.get(key, None)
        except Exception as e:
            st.error(f"Failed to read setting '{key}': {e}")
            return None

    def ReadFflagsConfig(self, flag_name):
        """Read a value from the fflags section of the Sober config."""
        file_path = os.path.expanduser("~/.var/app/org.vinegarhq.Sober/config/sober/config.json")
        try:
            with open(file_path, "r") as f:
                config = json.load(f)
            fflags = config.get("fflags", {})
            return fflags.get(flag_name, None)
        except Exception as e:
            st.error(f"Failed to read fflag '{flag_name}': {e}")
            return None

    def DeleteFflag(self, flag_name):
        """Delete a key from the fflags section of the Sober config."""
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
                st.warning(f"Flag '{flag_name}' not found in fflags.")
                return False
        except Exception as e:
            st.error(f"Failed to delete fflag '{flag_name}': {e}")
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
            st.success(f"fflags['{flag_name}'] set to {flag_value}")
        except Exception as e:
            st.error(f"Failed to update fflags: {e}")

    def UpdateSoberConfig(self, key, value):
        file_path = os.path.expanduser("~/.var/app/org.vinegarhq.Sober/config/sober/config.json")
        try:
            with open(file_path, "r") as f:
                config = json.load(f)
            config[key] = value
            with open(file_path, "w") as f:
                json.dump(config, f, indent=4)
            st.success(f"Config['{key}'] set to {value}")
        except Exception as e:
            st.error(f"Failed to update config: {e}")

    def CombineJson(self, *json_objs):
        """
        Combine multiple JSON objects (dicts) into one.
        Later objects overwrite earlier ones for duplicate keys.
        Skips any argument that is not a dict.
        """
        result = {}
        for obj in json_objs:
            if isinstance(obj, dict):
                result.update(obj)
            else:
                st.warning(f"Skipped non-dict object in CombineJson: {type(obj)}")
        return result

    def ReadLutionConfig(self, key, filename="LutionConfig.toml", default=None):
        from modules.utils.files import FilesFunctions
        ff = FilesFunctions()

        ff.JsonSetup()
        file_path = os.path.join(os.path.expanduser("~/Documents/Lution"), filename)
        if not os.path.exists(file_path):
            return default
        with open(file_path, "r") as f:
            data = toml.load(f)
        return data.get(key, default)

    def UpdateLutionConfig(self, key, value, filename="LutionConfig.toml"):
        from modules.utils.files import FilesFunctions
        ff = FilesFunctions()
        
        ff.JsonSetup()
        file_path = os.path.join(os.path.expanduser("~/Documents/Lution"), filename)
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = toml.load(f)
        else:
            data = {}
        data[key] = value
        with open(file_path, "w") as f:
            toml.dump(data, f)

    def ReadLutionMarketplaceConfig(self, key, filename="Marketplace.toml", default=None):
        from modules.utils.files import FilesFunctions
        ff = FilesFunctions()

        ff.JsonSetup2()
        file_path = os.path.join(os.path.expanduser("~/Documents/Lution/Lution Marketplace/"), filename)
        if not os.path.exists(file_path):
            return default
        with open(file_path, "r") as f:
            data = toml.load(f)
        return data.get(key, default)

    def UpdateLutionMarketplaceConfig(self, key, value, filename="Marketplace.toml"):
        from modules.utils.files import FilesFunctions
        ff = FilesFunctions()

        ff.JsonSetup2()
        file_path = os.path.join(os.path.expanduser("~/Documents/Lution/Lution Marketplace/"), filename)
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = toml.load(f)
        else:
            data = {}
        data[key] = value
        with open(file_path, "w") as f:
            toml.dump(data, f)

    def RemoveLutionMarketplaceConfig(self, key, value_to_remove, filename="Marketplace.toml"):
        from modules.utils.files import FilesFunctions
        ff = FilesFunctions()

        ff.JsonSetup2()
        file_path = os.path.join(os.path.expanduser("~/Documents/Lution/Lution Marketplace/"), filename)
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = toml.load(f)
        else:
            data = {}
        if key in data:
            values = data[key].split(',')
            values = [v.strip() for v in values]
            if value_to_remove in values:
                values.remove(value_to_remove)
                data[key] = ','.join(values)
                with open(file_path, "w") as f:
                    toml.dump(data, f)
            else:
                print(f"Value '{value_to_remove}' not found in key '{key}'.") # debug
        else:
            print(f"Key '{key}' not found in the dictionary.")

    def Json2Toml(self, json_path, toml_path=None):
        if not os.path.isfile(json_path):
            raise FileNotFoundError(f"ermmm where tf is the json file: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        if toml_path is None:
            toml_path = os.path.splitext(json_path)[0] + ".toml"

        with open(toml_path, "w", encoding="utf-8") as f:
            toml.dump(json_data, f)
