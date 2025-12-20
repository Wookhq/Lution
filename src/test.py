from modules.config import Config
from pathlib import Path

config = Config(Path("test.toml"))
config.add_row("settings", "theme", "dark")
config.remove_row("settings", "theme")
config.save()
