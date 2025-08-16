import sys
import subprocess
import time
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl

def main():
    weebserver = subprocess.Popen(["streamlit", "run", "main.py"])
    time.sleep(2)

    app = QApplication(sys.argv)
    browser = QWebEngineView()
    browser.resize(1500, 768)
    browser.setWindowTitle("Lution - Windwon")
    browser.load(QUrl("http://localhost:8501"))
    browser.show()

    exitCode=app.exec()

    weebserver.terminate()
    weebserver.wait()
    
    sys.exit(exitCode)

if __name__ == '__main__':
    main()
