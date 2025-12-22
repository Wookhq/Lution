import subprocess
import sys
import webbrowser
from pathlib import Path
from time import sleep

import darkdetect
from PySide6.QtCore import QLocale, QObject, QThread, QTranslator, Signal, Slot
from PySide6.QtGui import QAction, QGuiApplication, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

import resources_rc
from modules.config import Config
from RinUI import RinUITranslator, RinUIWindow

SCRIPT_DIR = Path(__file__).parent
__version__ = "0.1.0"

cfg = Config(Path("LutionConfig.toml"))


class MarketplaceWorker(QThread):
    finished = Signal(list)
    error = Signal(str)

    def run(self):
        try:
            sleep(4)
            items = [
                {
                    "title": "Marketplace mod 1",
                    "desc": "seia",
                    "img": "qrc:/resources/images/mod1.png",
                },
                {
                    "title": "Marketplace mod 2",
                    "desc": "mika",
                    "img": "qrc:/resources/images/mod2.png",
                },
                {
                    "title": "Marketplace mod 3",
                    "desc": "nagisa",
                    "img": "qrc:/resources/images/mod3.png",
                },
            ]

            self.finished.emit(items)
        except Exception as e:
            self.error.emit(str(e))


class MenuSplash(RinUIWindow):
    def __init__(self):
        qml_file = SCRIPT_DIR / "resources" / "ui" / "splash.qml"
        super().__init__(str(qml_file))

        # register backend
        self.backend = Backend()
        self.backend.setBackendParent(self)
        self.engine.rootContext().setContextProperty("Backend", self.backend)


class AppInit(RinUIWindow):
    def __init__(self):
        qml_file = SCRIPT_DIR / "resources" / "ui" / "MainWindow.qml"
        super().__init__(str(qml_file))

        # register backend
        self.backend = Backend()
        self.backend.setBackendParent(self)
        self.engine.rootContext().setContextProperty("Backend", self.backend)

        # title
        self.setProperty("title", "LutionRT")

        QApplication.instance().setQuitOnLastWindowClosed(False)

        self.initTray()

    def initTray(self):
        icon = QIcon.fromTheme("application-x-executable")
        self.tray = QSystemTrayIcon(icon, QApplication.instance())

        menu = QMenu()
        about = QAction("LutionRT", QApplication.instance())
        show_action = QAction("Show", QApplication.instance())
        quit_action = QAction("Quit", QApplication.instance())

        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(QApplication.quit)

        menu.addAction(about)
        menu.addAction(show_action)
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)
        self.tray.show()
        self.tray.activated.connect(self.onTrayClick)

    def onTrayClick(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show()
            self.raise_()
            self.activateWindow()

    def closeEvent(self, event):
        event.ignore()
        self.hide()


class Backend(QObject):
    marketplaceReady = Signal(list)
    marketplaceError = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None

    def setBackendParent(self, parent):
        self.parent = parent

    @Slot(result=str)
    def getVersion(self):
        return __version__

    @Slot(str)
    def copyToClipboard(self, text):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)
        print(f"Copied: {text}")

    @Slot(result=bool)
    def isDark(self):
        t = darkdetect.theme()
        print("darkdetect:", t)
        return t == "Dark"

    @Slot(str)
    def openInBroswer(self, url):
        webbrowser.open(url=url)

    @Slot()
    def openModFolder(self):
        modpath = Path(
            "~/.var/app/org.vinegarhq.Sober/data/sober/asset_overlay"
        ).expanduser()
        subprocess.Popen(["xdg-open", str(modpath)])

    @Slot()
    def getMarketplaceItems(self):
        """Fetch marketplace items asynchronously"""
        # Clean up previous worker if exists
        if self.worker is not None:
            self.worker.finished.disconnect()
            self.worker.error.disconnect()
            self.worker.quit()
            self.worker.wait()

        self.worker = MarketplaceWorker()
        self.worker.finished.connect(self._onMarketplaceLoaded)
        self.worker.error.connect(self._onMarketplaceError)
        self.worker.start()

    @Slot(list)
    def _onMarketplaceLoaded(self, items):
        print(f"Marketplace loaded: {len(items)} items")
        self.marketplaceReady.emit(items)

        if self.worker:
            self.worker.quit()
            self.worker.wait()

    @Slot(str)
    def _onMarketplaceError(self, error):
        print(f"Marketplace error: {error}")
        self.marketplaceError.emit(error)

        if self.worker:
            self.worker.quit()
            self.worker.wait()

    @Slot(result=str)
    def getSystemLanguage(self):
        return QLocale.system().name()

    @Slot(result=str)
    def getLanguage(self):
        return cfg.get_row("Lutionconfig", "language")

    @Slot(str)
    def setLanguage(self, lang: str):
        global ui_translator, translator

        app = QApplication.instance()
        lang_path = SCRIPT_DIR / "resources" / "i18n" / f"{lang}.qm"

        if not lang_path.exists():
            lang = "en_US"
            lang_path = SCRIPT_DIR / "resources" / "i18n" / f"{lang}.qm"

        cfg.add_row("Lution", "language", lang)
        cfg.save()

        app.removeTranslator(ui_translator)
        app.removeTranslator(translator)

        ui_translator = RinUITranslator(QLocale(lang))
        translator = QTranslator()
        translator.load(str(lang_path))

        app.installTranslator(ui_translator)
        app.installTranslator(translator)

        self.parent.engine.retranslate()

    @Slot()
    def launchChroma(self):
        splash = self.parent
        splash.close()
        splash.deleteLater()

        self.app_window = AppInit()
        self.app_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    lang = cfg.get_row("Lutionconfig", "language")

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
