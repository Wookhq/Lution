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
from RinUI import RinUITranslator, RinUIWindow

SCRIPT_DIR = Path(__file__).parent


cfg = Config(Path("LutionConfig.toml"))
cfg.initConfig()


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

    window = MenuSplash()
    window.show()

    app.exec()
