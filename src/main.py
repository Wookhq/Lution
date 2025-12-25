import subprocess
import sys
import webbrowser
from pathlib import Path
from time import sleep
from tkinter.constants import NONE

import darkdetect
from PySide6.QtCore import (
    QLocale,
    QObject,
    QThread,
    QTranslator,
    Signal,
    Slot,
)
from PySide6.QtGui import QAction, QGuiApplication, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from modules.backend import AppInit, Backend
from modules.config import Config
from modules.launchmenu import LaunchMenu
from RinUI import RinUITranslator, RinUIWindow

SCRIPT_DIR = Path(__file__).parent


cfg = Config(Path("LutionConfig.toml"))
cfg.initConfig()
__version__ = "0.1.0"

print(f"""
    CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
    CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
    CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
    CCCCCCCCCCC                                CCCCC
    CCCCCCCCCCCCC                              CCCCC
    CCCCCCCCCCCCCCC                            CCCCC
    CCCCCCCCCCCCCCCC                           CCCCC
    CCCCCC CCCCCCCCCCC                         CCCCC
    CCCCCC   CCCCCCCCCCCCCCCCCCCCCCCCC         CCCCC
    CCCCCC    CCCCCCCCCCCCCCCCCCCCCCCC         CCCCC
    CCCCCC      CCCCCCCCCCCCCCCCCCCCCC         CCCCC
    CCCCCC       CCCCCCCCCCCCCCCCCCCCC         CCCCC
    CCCCCC       CCCCCCCCCCCCCCCCCCCCC         CCCCC                                 Lution Chroma
    CCCCCC       CCCCCCCCCCCCCCCCCCCCC         CCCCC                        Built by wookhq and contributors
    CCCCCC       CCCCCCCCCCCCCCCCCCCCC         CCCCC                                    v{__version__}
    CCCCCC       CCCCCCCCCCCCCCCCCCCCC         CCCCC
    CCCCCC       CCCCCCCCCCCCCCCCCCCCCC        CCCCC
    CCCCCC       CCCCCCCCCCCCCCCCCCCCCCCC      CCCCC
    CCCCCC       CCCCCCCCCCCCCCCCCCCCCCCCCC    CCCCC
    CCCCCC       CCCCCCCCCCCCCCCCCCCCCCCCCCCC  CCCCC
    CCCCCC                         CCCCCCCCCCC CCCCC
    CCCCCC                           CCCCCCCCCCCCCCC
    CCCCCC                            CCCCCCCCCCCCCC
    CCCCCC                              CCCCCCCCCCCC
    CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
    CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
""")


class MenuSplash(RinUIWindow):
    def __init__(self):
        qml_file = SCRIPT_DIR / "resources" / "ui" / "splash.qml"
        super().__init__(None)

        # register backend
        self.backend = Backend()
        self.backend.setBackendParent(self)
        self.engine.rootContext().setContextProperty("Backend", self.backend)

        self.load(str(qml_file))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    lang = cfg.get_row("Lution", "language")

    ui_translator = RinUITranslator(QLocale(lang))
    app.installTranslator(ui_translator)

    translator = QTranslator()
    lang_qm = f":/resources/i18n/{lang}.qm"

    if translator.load(lang_qm):
        app.installTranslator(translator)
    else:
        print("no language file, falling back to english")

    if "--quick-launch" in sys.argv:
        launchmenu = LaunchMenu()
        launchmenu.show()
    else:
        window = MenuSplash()
        window.show()

    app.exec()
