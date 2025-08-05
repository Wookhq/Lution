#src/Lution/modules/json/json.py
import json
import os
import streamlit as st


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

    def ReadLutionConfig(self, key, filename="LutionConfig.json", default=None):
        from modules.utils.files import FilesFunctions
        ff = FilesFunctions()

        ff.JsonSetup()
        file_path = os.path.join(os.path.expanduser("~/Documents/Lution"), filename)
        if not os.path.exists(file_path):
            return default
        with open(file_path, "r") as f:
            data = json.load(f)
        return data.get(key, default)

    def UpdateLutionConfig(self, key, value, filename="LutionConfig.json"):
        from modules.utils.files import FilesFunctions
        ff = FilesFunctions()
        
        ff.JsonSetup()
        file_path = os.path.join(os.path.expanduser("~/Documents/Lution"), filename)
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
        else:
            data = {}
        data[key] = value
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
