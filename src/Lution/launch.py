import sys
import subprocess
import time
import requests
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl

def waitready(url, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(0.3)
    return False

def main():
    weebserver = subprocess.Popen(["streamlit", "run", "main.py"])

    if not waitready("http://localhost:8501"):
        print("streamlit failed :(")
        weebserver.terminate()
        sys.exit(1)

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
