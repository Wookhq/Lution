import os
import subprocess
import webbrowser
from pathlib import Path
from time import sleep
from tkinter.constants import NONE

import darkdetect
from mod_genarator import hex_to_rgb, recolor_directory
from PySide6.QtCore import QLocale, QObject, QThread, QTranslator, Signal, Slot
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

import resources_rc
from modules.config import Config
from modules.marketplace import MarketplaceHelper
from modules.config.sober_config import SoberConfig
from modules.launchmenu import LaunchMenu
from modules.launchmenu.splashMan import SplashMan
from modules.mod.fontreplace import Replace
from modules.mod.patch import Patcher
from RinUI import RinUITranslator, RinUIWindow

SCRIPT_DIR = Path(__file__).parent.parent
cfg = Config()
sbcfg = SoberConfig()
mkh = MarketplaceHelper()
__version__ = "0.1.0"


class NameUpdate(QObject):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.running = True

    @Slot()
    def run(self):
        while self.running:
            try:
                self.cfg.reloadName()
                self.cfg.save()
            except Exception as e:
                print("cfg reload error:", e)

            for _ in range(600):
                if not self.running:
                    return
                sleep(1)

    def stop(self):
        self.running = False


class MarketplaceWorker(QThread):
    finished = Signal(dict)   # <-- dict, not list
    error = Signal(str)

    def run(self):
        try:
            items = {
                "Mods": [
                    {
                        "title": "Better Default",
                        "body": "It's your default roblox icons, website with a sort of metallic look and an editor in a grey dunes landscape.",
                        "image": "https://raw.githubusercontent.com/wookhq/Lution-marketplace/refs/heads/main/Assets/thumbnails/better-default.jpg",
                        "creator": "thefrenchguy4 on Gamebanana",
                        "status": "unstable",
                        "featured": False,
                        "id": "c9007043-ca0b-4e7e-8874-2ea7a3187416"
                    },
                    {
                        "title": "Content Deleted",
                        "body": "###########? #####.",
                        "image": "https://raw.githubusercontent.com/wookhq/Lution-marketplace/refs/heads/main/Assets/thumbnails/content-deleted.jpg",
                        "creator": "MistressDooM on Gamebanana",
                        "status": "stable",
                        "featured": True,
                        "id": "c977ae7a-c426-4134-928d-91642ed4aa3d"
                    },
                    {
                        "title": "Blue star theme",
                        "body": "A blue star themed mod for Roblox, featuring a blue star background and blue icons.",
                        "image": "https://raw.githubusercontent.com/wookhq/Lution-marketplace/refs/heads/main/Assets/thumbnails/blue-star-theme.png",
                        "creator": "thefrenchguy4 on Gamebanana",
                        "status": "unstable",
                        "featured": False,
                        "id": "04523508-84a2-4e7c-8fb6-7a7afcaa62a7"
                    },
                    {
                        "title": "L337",
                        "body": "Experience Roblox like a true haxx0r! Converts all text into basic leet.",
                        "image": "https://raw.githubusercontent.com/wookhq/Lution-marketplace/refs/heads/main/Assets/thumbnails/L337.png",
                        "creator": "MistressDooM on Gamebanana",
                        "status": "stable",
                        "featured": True,
                        "id": "cecfac23-d791-496f-9222-f696386ed9fb"
                    }
                ],
                "Theme": "None"
            }

            self.finished.emit(items)

        except Exception as e:
            self.error.emit(str(e))

class FontWorker(QThread):
    finished = Signal()
    error = Signal(str)

    def __init__(self, font_path):
        super().__init__()
        self.font_path = font_path

    def run(self):
        try:
            Patcher().patch()

            clean_path = self.font_path.replace("file://", "")

            Replace(
                clean_path,
                "/home/chip/.var/app/org.vinegarhq.Sober/data/sober/asset_overlay/content/fonts/",
            )

            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class ModGenWorker(QThread):
    finished = Signal()
    error = Signal(str)

    def __init__(self, hex_color):
        super().__init__()
        self.rgb_color = hex_to_rgb(hex_color)

    def run(self):
        try:
            os.makedirs(
                os.path.dirname(
                    os.path.expanduser(cfg.get_row("Sober", "Path")),
                ),
                exist_ok=True,
            )
            recolor_directory(
                os.path.expanduser(
                    f"{cfg.get_row('Sober', 'Path')}/data/sober/assets/ExtraContent/LuaPackages/Packages/_Index/BuilderIcons/BuilderIcons/Font/"
                ),
                self.rgb_color,
                os.path.expanduser(cfg.get_row("Sober", "Path")),
            )
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


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
        QApplication.instance().aboutToQuit.connect(self.backend.shutdown)

        # QApplication.instance().setQuitOnLastWindowClosed(False)

        # self.initTray()

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

    # def closeEvent(self, event):
    #   event.ignore()
    #   self.hide()


class Backend(QObject):
    marketplaceReady = Signal(dict)
    marketplaceError = Signal(str)
    fontApplied = Signal()
    fontError = Signal(str)
    modGen = Signal()
    modGenError = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.font_worker = None
        self.mod_worker = None
        self.ui_translator = None
        self.translator = None
        self.splashMan = SplashMan()

        self.cfg_thread = QThread()
        self.cfg_worker = NameUpdate(cfg)
        self.cfg_worker.moveToThread(self.cfg_thread)
        self.cfg_thread.started.connect(self.cfg_worker.run)
        self.cfg_thread.start()

    def setBackendParent(self, parent):
        self.parent = parent

    def shutdown(self):
        if self.cfg_worker:
            self.cfg_worker.stop()
        if self.cfg_thread:
            self.cfg_thread.quit()
            self.cfg_thread.wait()

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

    @Slot(result=str)
    def getName(self):
        cfg.reload()
        return cfg.get_row("Misc", "UserDisplayName")

    @Slot()
    def openModFolder(self):
        modpath = Path(
            "~/.var/app/org.vinegarhq.Sober/data/sober/asset_overlay"
        ).expanduser()
        subprocess.Popen(["xdg-open", str(modpath)])


    @Slot(result=str)
    def getMarketplaceProvider(self):
        return cfg.get_row("Lution", "MarketplaceRepo")
    
    @Slot(result=str)
    def getGithubAPIKey(self):
        return cfg.get_row("Lution", "GithubKeyAPI")
    
    @Slot(str)
    def setMarketplaceProvider(self, provider):
        cfg.get_row("Lution", "MarketplaceRepo", provider)
        cfg.save()
    
    @Slot(str)
    def setGithubAPIKey(self, key):
        cfg.add_row("Lution", "GithubKeyAPI", key)
        cfg.save()

    @Slot()
    def getMarketplaceItems(self):
        if self.worker is not None:
            self.worker.finished.disconnect()
            self.worker.error.disconnect()
            self.worker.quit()
            self.worker.wait()

        self.worker = MarketplaceWorker()
        self.worker.finished.connect(self._onMarketplaceLoaded)
        self.worker.error.connect(self._onMarketplaceError)
        self.worker.start()

    @Slot(result="QVariant")
    def getSplash(self):
        return self.splashMan.getSplash()

    @Slot(result=str)
    def getSoberPath(self):
        return cfg.get_row("Sober", "Path")

    @Slot(str)
    def setSoberPath(self, path):
        if path:
            cfg.remove_row("Sober", "Path")
            cfg.add_row("Sober", "Path", path)
            cfg.save()
        else:
            cfg.remove_row("Sober", "Path")
            cfg.add_row("Sober", "Path", "~/.var/app/org.vinegarhq.Sober")
            cfg.save()

    @Slot(str)
    def setFont(self, path):
        if self.font_worker is not None:
            self.font_worker.finished.disconnect()
            self.font_worker.error.disconnect()
            self.font_worker.quit()
            self.font_worker.wait()

        print(f"Starting font application: {path}")

        self.font_worker = FontWorker(path)
        self.font_worker.finished.connect(self._onFontApplied)
        self.font_worker.error.connect(self._onFontError)
        self.font_worker.start()

    @Slot()
    def _onFontApplied(self):
        print("Font applied successfully")
        self.fontApplied.emit()

        if self.font_worker:
            self.font_worker.quit()
            self.font_worker.wait()

    @Slot(str)
    def _onFontError(self, error):
        print(f"Font application error: {error}")
        self.fontError.emit(error)

        if self.font_worker:
            self.font_worker.quit()
            self.font_worker.wait()

    @Slot(result=str)
    def getCurrentSplash(self):
        return self.splashMan.getCurrentSplash()

    @Slot(str)
    def setSplash(self, name):
        self.splashMan.setSplash(name)

    @Slot(str, "QVariant")
    def addSoberKey(self, key, value):
        sbcfg.write_key(key, value)

    @Slot(str, result="QVariant")
    def getSoberKey(self, key):
        return sbcfg.read_key(key)

    @Slot(dict)
    def _onMarketplaceLoaded(self, items):
        print(f"Marketplace loaded: {len(items.get('Mods', []))} mods")
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

    @Slot(str)
    def genarateMod(self, hex_color):
        if self.mod_worker is not None:
            self.mod_worker.finished.disconnect()
            self.mod_worker.error.disconnect()
            self.mod_worker.quit()
            self.mod_worker.wait()

        print(f"Genarating mod with hex color: {hex_color}")

        self.mod_worker = ModGenWorker(hex_color)
        self.mod_worker.finished.connect(self._onModGenSucess)
        self.mod_worker.error.connect(self._onModGenError)
        self.mod_worker.start()

    @Slot()
    def _onModGenSucess(self):
        print("Mod genarated successfully")
        self.modGen.emit()

        if self.mod_worker:
            self.mod_worker.quit()
            self.mod_worker.wait()

    @Slot(str)
    def _onModGenError(self, error):
        print(f"Mod genaration error: {error}")
        self.modGenError.emit(error)

        if self.mod_worker:
            self.mod_worker.quit()
            self.mod_worker.wait()

    @Slot(result=str)
    def getSystemLanguage(self):
        return QLocale.system().name()

    @Slot(result=str)
    def getLanguage(self):
        return cfg.get_row("Lutionconfig", "language")

    @Slot(str)
    def setLanguage(self, lang: str):
        app = QApplication.instance()
        lang_path = SCRIPT_DIR / "resources" / "i18n" / f"{lang}.qm"

        if not lang_path.exists():
            lang = "en_US"
            lang_path = SCRIPT_DIR / "resources" / "i18n" / f"{lang}.qm"

        cfg.add_row("Lution", "language", lang)
        cfg.save()

        if self.ui_translator:
            app.removeTranslator(self.ui_translator)
        if self.translator:
            app.removeTranslator(self.translator)

        self.ui_translator = RinUITranslator(QLocale(lang))
        self.translator = QTranslator()
        self.translator.load(str(lang_path))

        app.installTranslator(self.ui_translator)
        app.installTranslator(self.translator)

        self.parent.engine.retranslate()

    @Slot()
    def launchChroma(self):
        splash = self.parent
        splash.close()
        splash.deleteLater()

        self.app_window = AppInit()
        self.app_window.show()

    @Slot()
    def launchMenu(self):
        splash = self.parent
        splash.close()
        splash.deleteLater()

        self.launch_menu = LaunchMenu()
        self.launch_menu.show()
