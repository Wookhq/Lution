
from PySide6.QtCore import Property, QThread, Signal, Slot, QObject
from PySide6.QtWidgets import QApplication
import subprocess
import darkdetect
from pathlib import Path
import resources_rc
import re
from time import sleep
from PySide6.QtGui import QGuiApplication
from RinUI import RinUIWindow


__version__ = "0.1.0"

class LaunchSplashChecks(QThread):
    progressUpdate = Signal(str)
    finished = Signal(bool)
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self._cancel_requested = False
        self._process = None

    def cancel(self):
        self._cancel_requested = True
        if self._process:
            self._process.terminate()
            self._process.wait(timeout=5)
            if self._process.poll() is None:
                self._process.kill()

    def run(self):
        try:
            if self._cancel_requested:
                return

            self.progressUpdate.emit("Checking For Updates")
            command = ["flatpak", "remote-ls", "--updates"]

            result = subprocess.run(command, capture_output=True, text=True)

            if self._cancel_requested:
                return

            if "org.vinegarhq.Sober" in result.stdout:
                self.progressUpdate.emit("Update available! Auto updating...")
                sleep(3)

                if self._cancel_requested:
                    return

                command = ["flatpak", "update", "-y", "--app", "org.vinegarhq.Sober"]
                self._process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )

                pattern = re.compile(r"Updating\s+(\d+/\d+)")

                for line in self._process.stdout:
                    if self._cancel_requested:
                        self._process.terminate()
                        return

                    line = line.strip()
                    match = pattern.search(line)
                    if match:
                        step = match.group(1)
                        self.progressUpdate.emit(f"Update progress: {step}")

                self._process.wait()
                self._process = None

                if self._cancel_requested:
                    return

                self.progressUpdate.emit("Updated!")
                sleep(3)

            if self._cancel_requested:
                return

            self.progressUpdate.emit("Launching Sober...")
            sleep(10)

            command = ["flatpak", "run", "org.vinegarhq.Sober"]

            subprocess.Popen(command)

            self.finished.emit(True)
        except Exception as e:
            if not self._cancel_requested:
                self.error.emit(str(e))
                self.finished.emit(False)


class LaunchSplashBackend(QObject):
    progressText = Signal()
    checksComplete = Signal(bool)
    checksError = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress_text = "Initializing..."
        self.worker = None

    def setBackendParent(self, parent):
        self.parent = parent

    @Property(str, notify=progressText)
    def progress(self):
        return self._progress_text

    def setProgressText(self, value):
        self._progress_text = value
        self.progressText.emit()

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

    @Slot()
    def cancel(self):
        if self.worker:
            self.worker.cancel()
            self.worker.wait(2000)
            if self.worker.isRunning():
                self.worker.terminate()
                self.worker.wait()
        window = self.parent
        window.close()
        QApplication.quit()

    @Slot()
    def startChecks(self):
        if self.worker is not None:
            self.worker.progressUpdate.disconnect()
            self.worker.finished.disconnect()
            self.worker.error.disconnect()
            self.worker.cancel()
            self.worker.wait()

        self.worker = LaunchSplashChecks()
        self.worker.progressUpdate.connect(self._onProgressUpdate)
        self.worker.finished.connect(self._onChecksComplete)
        self.worker.error.connect(self._onChecksError)
        self.worker.start()

    @Slot(str)
    def _onProgressUpdate(self, text):
        print(f"Progress: {text}")
        self.setProgressText(text)

    @Slot(bool)
    def _onChecksComplete(self, success):
        print(f"Checks complete: {success}")
        self.checksComplete.emit(success)

        if self.worker:
            self.worker.wait()

    @Slot(str)
    def _onChecksError(self, error):
        print(f"Checks error: {error}")
        self.checksError.emit(error)

        if self.worker:
            self.worker.wait()


from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

class LaunchMenu(RinUIWindow):
    def __init__(self):
        qml_file = SCRIPT_DIR.parent.parent / "resources" / "ui" / "DefaultSplash" / "Calling.qml"

        super().__init__(None)  # do NOT load qml yet

        self.backend = LaunchSplashBackend()
        self.backend.setBackendParent(self)

        self.engine.rootContext().setContextProperty("Backend", self.backend)

        self.load(str(qml_file))  # NOW load qml

