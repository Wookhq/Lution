import json
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
