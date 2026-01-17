# splash manager
from pathlib import Path

from modules.config import Config

cfg = Config()


class SplashMan:
    def __init__(self) -> None:
        pass

    def getSplash(self):
        return cfg.get_row("LutionSplash", "Splashs")

    def getCurrentSplash(self):
        return cfg.get_row("LutionSplash", "CurrentSplash")

    def setSplash(self, name):
        cfg.remove_row("LutionSplash", "CurrentSplash")
        cfg.add_row("LutionSplash", "CurrentSplash", name)
        cfg.save()
