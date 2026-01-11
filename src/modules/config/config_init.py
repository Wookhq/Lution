import datetime

from modules.config import Config
from modules.utils.namegrabber import getUserIdFromLogs, getName

cfg = Config()


def reloadName():
    try:
        cfg.add_row("Misc", "UserDisplayName", getName(getUserIdFromLogs()))
    except Exception:
        print("not logged in")
        cfg.add_row("Misc", "UserDisplayName", "User")
    cfg.add_row("Misc", "LastUpdated", datetime.datetime.now())


def initConfig():
    if not cfg.get_row("Lution", "FirstTimeLaunch"):
        cfg.add_row("Lution", "language", "en_US")
        cfg.add_row("LutionSplash", "CurrentSplash", "Default")
        cfg.add_row("Lution", "MarketplaceRepo", "wookhq/Chroma-Marketplace")
        cfg.add_row("Lution", "GithubKeyAPI", "None")

        cfg.add_row(
            "LutionSplash", "Splashs", ["Default", "Calling", "Terminal", "Sober"]
        )  # hard coded for now
        cfg.add_row("Lution", "FirstTimeLaunch", "False")
        cfg.add_row("Sober", "Path", "~/.var/app/org.vinegarhq.Sober")
        cfg.save()
        try:
            cfg.add_row("Misc", "UserDisplayName", getName(getUserIdFromLogs()))
        except Exception:
            print("not logged in")
            cfg.add_row("Misc", "UserDisplayName", "User")

        cfg.add_row("Misc", "LastUpdated", datetime.datetime.now())
        cfg.save()
    else:
        return
