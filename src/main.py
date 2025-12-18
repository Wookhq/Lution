import sys, os, webbrowser
import darkdetect  # installed in rinui
from pathlib import Path
import subprocess
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Signal, QObject, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from RinUI import RinUIWindow
import resources_rc

SCRIPT_DIR = Path(__file__).parent
__version__ = "0.1.0"


# rcs = Resource(SCRIPT_DIR=SCRIPT_DIR)  # new method


class AppInit(RinUIWindow):
    def __init__(self):
        qml_file = SCRIPT_DIR / "resources" / "ui" / "MainWindow.qml"
        super().__init__(str(qml_file))


        # backend
        self.backend = Backend()
        self.backend.setBackendParent(self)
        self.engine.rootContext().setContextProperty("Backend", self.backend)

        # title
        self.setProperty("title", "LutionRT")
        
        QApplication.instance().setQuitOnLastWindowClosed(False)

        self.initTray()

    def initTray(self):
        icon = QIcon.fromTheme(
            "application-x-executable",
        )


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
    clipsReady = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.rpc = VimalPresence("1442032843290181703") as you can tell this code is from vimal
        # self.resc = rcs

    # @Slot(str, str)
    # def setPresence(self, state, details):
    #     print("woops presence changed, presence setin!!!!")
    #     self.rpc.set(state=state, details=details)  # so confusing mate

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

    @Slot(str, result=str)
    def findResource(self, resource):
        return self.resc.find(resource)
    
    @Slot(str)
    def openInBroswer(self, url):
        webbrowser.open(url=url)

    @Slot()
    def openModFolder(self):
        modpath = Path("~/.var/app/org.vinegarhq.Sober/data/sober/asset_overlay").expanduser()
        subprocess.Popen(["xdg-open", str(modpath)])




if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = AppInit()
    window.show()
    app.exec()