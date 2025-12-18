import sys, os
import darkdetect  # installed in rinui
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Signal, QObject, Slot
from PySide6.QtGui import QGuiApplication
from RinUI import RinUIWindow

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





class Backend(QObject):
    clipsReady = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.rpc = VimalPresence("1442032843290181703")
        # self.resc = rcs

    # @Slot(str, str)
    # def setPresence(self, state, details):
    #     print("woops presence changed, presence setin!!!!")
    #     self.rpc.set(state=state, details=details)  # so confusing mate

    def setBackendParent(self, parent):
        self.parent = parent

    @Slot()
    def getClips(self):
        self.parent.load_clips()

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


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = AppInit()
    window.show()
    app.exec()