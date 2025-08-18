from typing import Optional
from pathlib import Path
import sys
import os


FROZEN: bool = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")

def _get_known_folder_path(uuidstr):
    # https://stackoverflow.com/a/35851955
    import ctypes
    from ctypes import windll, wintypes
    from uuid import UUID

    # ctypes GUID copied from MSDN sample code
    class GUID(ctypes.Structure):
        _fields_ = [
            ("Data1", wintypes.DWORD),
            ("Data2", wintypes.WORD),
            ("Data3", wintypes.WORD),
            ("Data4", wintypes.BYTE * 8)
        ] 

        def __init__(self, uuidstr):
            uuid = UUID(uuidstr)
            ctypes.Structure.__init__(self)
            self.Data1, self.Data2, self.Data3, \
                self.Data4[0], self.Data4[1], rest = uuid.fields
            for i in range(2, 8):
                self.Data4[i] = rest>>(8-i-1)*8 & 0xff

    SHGetKnownFolderPath = windll.shell32.SHGetKnownFolderPath
    SHGetKnownFolderPath.argtypes = [
        ctypes.POINTER(GUID), wintypes.DWORD,
        wintypes.HANDLE, ctypes.POINTER(ctypes.c_wchar_p)
    ]

    pathptr = ctypes.c_wchar_p()
    guid = GUID(uuidstr)
    if SHGetKnownFolderPath(ctypes.byref(guid), 0, 0, ctypes.byref(pathptr)):
        raise ctypes.WinError()
    return pathptr.value


def _get_downloads_directory() -> Path:
    home: Path = Path.home()
    fallback: Path = home / "Downloads" if (home / "Downloads").exists() else home
    if os.name != "nt": return fallback

    try:
        FOLDERID_Download = '{374DE290-123F-4565-9164-39C4925E467B}'
        return Path(_get_known_folder_path(FOLDERID_Download))

    except Exception: return fallback


def _get_desktop_directory() -> Path:
    home: Path = Path.home()
    fallback: Path = home / "Desktop"
    if os.name != "nt": return fallback

    try:
        FOLDERID_Download = '{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}'
        return Path(_get_known_folder_path(FOLDERID_Download))

    except Exception: return fallback


class Directories:
    ROOT: Path = (Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent.parent.parent).resolve()
    CRASHES: Path = ROOT / "Crashes"
    CONFIG: Path = ROOT / "config"
    CACHE: Path = ROOT / "cache"
    SHORTCUTS_CACHE: Path = CACHE / "shortcuts"
    SHORTCUTS_DESKTOP_ICON_CACHE: Path = CACHE / "shortcuts" / "desktop_icons"
    MEIPASS: Optional[Path] = Path(sys._MEIPASS) if FROZEN else None  # type: ignore
    RESOURCES: Path = (MEIPASS if FROZEN else ROOT) / "resources"  # type: ignore
    MOD_GENERATOR_FILES: Path = RESOURCES / "mod_generator_files"
    OUTPUT_DIR: Path = ROOT / "output"
    OUTPUT_DIR_GENERATOR: Path = OUTPUT_DIR / "generator"
    OUTPUT_DIR_UPDATER: Path = OUTPUT_DIR / "updater"

    BLOXSTRAP_MOD: Path = Path.home() / "AppData" / "Local" / "Bloxstrap" / "Modifications"
    FISHSTRAP_MOD: Path = Path.home() / "AppData" / "Local" / "Fishstrap" / "Modifications"

    DOWNLOADS: Path = _get_downloads_directory().resolve()
    DESKTOP: Path = _get_desktop_directory().resolve()


class Files:
    CONFIG: Path = Directories.CONFIG / "config.json"
    SHORTCUTS_CONFIG: Path = Directories.CONFIG / "shortcuts.json"
    SHORTCUTS_CACHE_INDEX: Path = Directories.SHORTCUTS_CACHE / "index.json"


class Resources:
    FAVICON: Path = Directories.RESOURCES / "favicon.ico"
    BANNER: Path = Directories.RESOURCES / "banner.png"

    class Logo:
        DEFAULT: Path = Directories.RESOURCES / "logo" / "default.png"

    class Common:
        class Light:
            BIN: Path = Directories.RESOURCES / "common" / "light" / "bin.png"
            SUCCESS: Path = Directories.RESOURCES / "common" / "light" / "success.png"
            WARNING: Path = Directories.RESOURCES / "common" / "light" / "warning.png"
            ERROR: Path = Directories.RESOURCES / "common" / "light" / "error.png"
            ATTENTION: Path = Directories.RESOURCES / "common" / "light" / "attention.png"
            INFO: Path = Directories.RESOURCES / "common" / "light" / "info.png"
            CLOSE: Path = Directories.RESOURCES / "common" / "light" / "close.png"
            ARROW_RIGHT: Path = Directories.RESOURCES / "common" / "light" / "arrow_right.png"
            EYE: Path = Directories.RESOURCES / "common" / "light" / "eye.png"
            ADD: Path = Directories.RESOURCES / "common" / "light" / "add.png"
            START: Path = Directories.RESOURCES / "common" / "light" / "start.png"
            RESET: Path = Directories.RESOURCES / "common" / "light" / "reset.png"
            STOP: Path = Directories.RESOURCES / "common" / "light" / "stop.png"
        class Dark:
            BIN: Path = Directories.RESOURCES / "common" / "dark" / "bin.png"
            SUCCESS: Path = Directories.RESOURCES / "common" / "dark" / "success.png"
            WARNING: Path = Directories.RESOURCES / "common" / "dark" / "warning.png"
            ERROR: Path = Directories.RESOURCES / "common" / "dark" / "error.png"
            ATTENTION: Path = Directories.RESOURCES / "common" / "dark" / "attention.png"
            INFO: Path = Directories.RESOURCES / "common" / "dark" / "info.png"
            CLOSE: Path = Directories.RESOURCES / "common" / "dark" / "close.png"
            ARROW_RIGHT: Path = Directories.RESOURCES / "common" / "dark" / "arrow_right.png"
            EYE: Path = Directories.RESOURCES / "common" / "dark" / "eye.png"
            ADD: Path = Directories.RESOURCES / "common" / "dark" / "add.png"
            START: Path = Directories.RESOURCES / "common" / "dark" / "start.png"
            RESET: Path = Directories.RESOURCES / "common" / "dark" / "reset.png"
            STOP: Path = Directories.RESOURCES / "common" / "dark" / "stop.png"

    class Navigation:
        class Light:
            MOD_UPDATER: Path = Directories.RESOURCES / "nav" / "light" / "mod_updater.png"
            MOD_GENERATOR: Path = Directories.RESOURCES / "nav" / "light" / "mod_generator.png"
            SHORTCUTS: Path = Directories.RESOURCES / "nav" / "light" / "shortcuts.png"
            SETTINGS: Path = Directories.RESOURCES / "nav" / "light" / "settings.png"
            ABOUT: Path = Directories.RESOURCES / "nav" / "light" / "about.png"
        class Dark:
            MOD_UPDATER: Path = Directories.RESOURCES / "nav" / "dark" / "mod_updater.png"
            MOD_GENERATOR: Path = Directories.RESOURCES / "nav" / "dark" / "mod_generator.png"
            SHORTCUTS: Path = Directories.RESOURCES / "nav" / "dark" / "shortcuts.png"
            SETTINGS: Path = Directories.RESOURCES / "nav" / "dark" / "settings.png"
            ABOUT: Path = Directories.RESOURCES / "nav" / "dark" / "about.png"

    class Shortcuts:
        class Light:
            PLACEHOLDER: Path = Directories.RESOURCES / "shortcuts" / "light" / "placeholder.png"
        class Dark:
            PLACEHOLDER: Path = Directories.RESOURCES / "shortcuts" / "dark" / "placeholder.png"

    class Brands:
        class Light:
            GITHUB: Path = Directories.RESOURCES / "brands" / "light" / "github.png"
            DISCORD: Path = Directories.RESOURCES / "brands" / "light" / "discord.png"
        class Dark:
            GITHUB: Path = Directories.RESOURCES / "brands" / "dark" / "github.png"
            DISCORD: Path = Directories.RESOURCES / "brands" / "dark" / "discord.png"
        class Normal:
            GITHUB: Path = Directories.RESOURCES / "brands" / "normal" / "github.png"
            DISCORD: Path = Directories.RESOURCES / "brands" / "normal" / "discord.png"

    class ColorPicker:
        SATURATION_VALUE: Path = Directories.RESOURCES / "color_picker" / "saturation_value.png"
        HUE: Path = Directories.RESOURCES / "color_picker" / "hue.png"
        INDICATOR: Path = Directories.RESOURCES / "color_picker" / "indicator.png"
        INDICATOR_WIDE: Path = Directories.RESOURCES / "color_picker" / "indicator_wide.png"