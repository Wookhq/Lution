import json
import zipfile
import shutil
from pathlib import Path
from modules.utils.logging import log
from modules.config.genconfig import Config
from modules.utils.files import FilesFunctions

cg = Config()
lg = log()
ff = FilesFunctions()  # FREE FIRE :fire:


class crossover:
    def __init__(self):
        pass

    def crossover(self, folder: str | Path):
        folder = Path(folder)

        if not folder.exists() or not folder.is_dir():
            lg.error(f"CROSSOVER : Folder not found at {folder}")
            return

        config_file = folder / "crossover.json"
        if not config_file.exists():
            lg.error(f"CROSSOVER : crossover.json not found in {folder}")
            return

        try:
            content = json.loads(config_file.read_text(encoding="utf-8"))

            lg.info(
                f"Using crossover version {content['metadata']['crossoverVerison']}"
            )
            lg.info(f"CROSSOVER : Platform {content['metadata']['roblox']}")

            fastflagpath = content.get("crossover", {}).get("fastflag", "none")
            if fastflagpath == "none":
                lg.info("CROSSOVER : Did not find fastflag")
                fastflag_file = None
            else:
                lg.info(f"CROSSOVER : Found fastflag path : {fastflagpath}")
                fastflag_file = folder / fastflagpath

            mod = content.get("crossover", {}).get("mod", "none")
            if mod == "none":
                lg.info("CROSSOVER : Did not find mod")
                mod_path = None
            else:
                lg.info(f"CROSSOVER : Found mod path : {mod}")
                mod_path = folder / mod

            lg.info("CROSSOVER : Crossing over!")

            if fastflag_file and fastflag_file.exists():
                try:
                    lg.info("CROSSOVER : Trying overwrite Fast Flag...")

                    try:
                        fastflagcontent = json.loads(
                            fastflag_file.read_text(encoding="utf-8")
                        )

                        cg.UpdateSoberConfig("fflags", fastflagcontent)
                    except json.JSONDecodeError as e:
                        lg.error(f"CROSSOVER : Fastflag file is not valid JSON -> {e}")

                except Exception as e:
                    lg.error(f"Unknown error : {e}")
            elif fastflag_file:
                lg.error(f"CROSSOVER : Fastflag file not found at {fastflag_file}")

            if mod_path:
                try:
                    lg.info("CROSSOVER : Applying mods ...")
                    ff.ApplyMarketplaceMods(mod_path)

                except Exception as e:
                    lg.error(f"Unkown error : {e}")
            
        except KeyError as e:
            lg.error(f"Missing key: {e}")
            return f"Missing {e}"
    
    def create(self, folder: str | Path, roblox_platform: str = "android", crossover_version: int = 1):
        folder = Path(folder).expanduser()
        folder.mkdir(parents=True, exist_ok=True)

        lg.info(f"CROSSOVER CREATE : Creating new crossover folder at {folder}")

        crossover_json = {
            "metadata": {
                "crossoverVerison": crossover_version,
                "from": "linux",
                "roblox": roblox_platform,
                "date": "unknown"
            },
            "crossover": {
                "fastflag": "./roblox/clientsettings/ClientSettings.json",
                "mod": "./roblox/mod/"
            }
        }

        crossover_file = folder / "crossover.json"
        crossover_file.write_text(json.dumps(crossover_json, indent=4), encoding="utf-8")
        lg.info(f"CROSSOVER CREATE : Wrote crossover.json at {crossover_file}")

        clientsettings_folder = folder / "roblox" / "clientsettings"
        clientsettings_folder.mkdir(parents=True, exist_ok=True)

        mod_folder = folder / "roblox" / "mod"
        mod_folder.mkdir(parents=True, exist_ok=True)

        source_mods = Path("~/.var/app/org.vinegarhq.Sober/data/sober/asset_overlay/").expanduser()
        if source_mods.exists() and source_mods.is_dir():
            lg.info(f"CROSSOVER CREATE : Copying mods from {source_mods} to {mod_folder}")
            for item in source_mods.iterdir():
                dest = mod_folder / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)
        else:
            lg.info(f"CROSSOVER CREATE : No mods found in {source_mods}")

        clientsettings = cg.ReadSoberConfig('fflags')
        dump = json.dumps(clientsettings, indent=4)
        (clientsettings_folder / "ClientSettings.json").write_text(dump, encoding="utf-8")
        lg.info(f"CROSSOVER CREATE : Created placeholder ClientSettings.json")

        lg.info(f"CROSSOVER CREATE : Created mod folder at {mod_folder}")

        return folder

    def pack(self, folder: str | Path):
        folder = Path(folder)
        if not folder.exists() or not folder.is_dir():
            lg.error(f"CROSSOVER PACK : Folder not found at {folder}")
            return

        crossover_file = folder.with_suffix(".crossover")  
        lg.info(f"CROSSOVER PACK : Creating {crossover_file}")

        with zipfile.ZipFile(crossover_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in folder.rglob("*"):
                zf.write(file, arcname=file.relative_to(folder))
        
        lg.info(f"CROSSOVER PACK : Finished packing {crossover_file}")
        return crossover_file
    
    def unpack(self, crossover_file: str | Path, dest_folder: str | Path = None):
        crossover_file = Path(crossover_file)
        if not crossover_file.exists() or crossover_file.suffix != ".crossover":
            lg.error(f"CROSSOVER UNPACK : File not found or invalid extension {crossover_file}")
            return

        if dest_folder is None:
            dest_folder = crossover_file.with_suffix("") 
        else:
            dest_folder = Path(dest_folder)

        dest_folder.mkdir(parents=True, exist_ok=True)
        lg.info(f"CROSSOVER UNPACK : Extracting {crossover_file} to {dest_folder}")

        with zipfile.ZipFile(crossover_file, "r") as zf:
            zf.extractall(dest_folder)

        lg.info(f"CROSSOVER UNPACK : Finished extracting to {dest_folder}")
        return dest_folder