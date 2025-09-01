import sys
import subprocess
import re
import datetime
import threading
import csv
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QPushButton
from PySide6.QtGui import QAction, QIcon
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QEvent, Signal, QObject

chat_pattern = re.compile(r"Success Text: (.*)")
player_pattern = re.compile(r"Player (added|removed): (.+) (\d+)")
chat_player_pattern = re.compile(r"Player (\d+): (.+)")

def timestamp():
    return datetime.datetime.now().strftime("%H:%M:%S")

class MainApp(QObject):
    finished_signal = Signal()

    def __init__(self):
        super().__init__()
        

        loader = QUiLoader()
        ui_file = QFile("files/playerlogs.ui")
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file)
        ui_file.close()

        self.window.hide()

        self.window.closeEvent = self.closeEvent

        # map user id -> player name
        self.players = {}

        # chats table setup
        self.chat_table = self.window.findChild(QTableWidget, "chatTable")
        self.chat_table.setColumnCount(3)
        self.chat_table.setHorizontalHeaderLabels(["Time", "Player", "Message"])
        self.chat_table.setColumnWidth(0, 80)
        self.chat_table.setColumnWidth(1, 160)

        # joins/leaves table setup
        self.join_table = self.window.findChild(QTableWidget, "joinTable")
        if self.join_table:
            self.join_table.setColumnCount(3)
            self.join_table.setHorizontalHeaderLabels(["Time", "Player", "Action"])
            self.join_table.setColumnWidth(0, 80)
            self.join_table.setColumnWidth(1, 160)

        # tray icon setup
        self.tray = QSystemTrayIcon(QIcon.fromTheme("applications-games"))
        self.tray.setToolTip("Lution")

        menu = QMenu()
        show_logs_action = QAction("Show Logs")
        save_action = QAction("Save Logs")
        exit_action = QAction("Exit")

        show_logs_action.triggered.connect(self.window.show)
        save_action.triggered.connect(self.save_logs)
        exit_action.triggered.connect(lambda: sys.exit(0))

        menu.addAction(show_logs_action)
        menu.addAction(save_action)
        menu.addAction(exit_action)

        self.tray.setContextMenu(menu)

        def on_tray_activated(reason):
            if reason == QSystemTrayIcon.Trigger:  # left click
                self.window.show()
            elif reason == QSystemTrayIcon.Context: # right click
                menu.exec(self.tray.geometry().center())

        self.tray.activated.connect(on_tray_activated)
        self.tray.show()

        self.finished_signal.connect(QApplication.instance().quit)
        
        self.save_button = self.window.findChild(QPushButton, "pushButton")
        if self.save_button:
            self.save_button.clicked.connect(self.save_logs)

        threading.Thread(target=self.launch_and_watch, daemon=True).start()

    def closeEvent(self, event):
        event.ignore()
        self.window.hide()
    
    def save_logs(self):
        default_filename = f"LutionLogs_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        file_path, _ = QFileDialog.getSaveFileName(self.window, "Save Logs", default_filename, "CSV Files (*.csv)")

        if not file_path:
            return  

        try:
            self._save_table_to_csv(self.chat_table, f"{file_path}_chat.csv")
            
            if self.join_table:
                self._save_table_to_csv(self.join_table, f"{file_path}_join.csv")
            
            QMessageBox.information(self.window, "Save Successful", f"Logs saved successfully to {file_path}_chat.csv and {file_path}_join.csv.")
        except Exception as e:
            QMessageBox.critical(self.window, "Save Failed", f"An error occurred while saving the logs: {e}")

    def _save_table_to_csv(self, table, filename):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            header = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
            writer.writerow(header)
            
            for row in range(table.rowCount()):
                row_data = []
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    row_data.append(item.text() if item is not None else "")
                writer.writerow(row_data)

    def add_chat_row(self, player, message):
        row = self.chat_table.rowCount()
        self.chat_table.insertRow(row)
        self.chat_table.setItem(row, 0, QTableWidgetItem(timestamp()))
        self.chat_table.setItem(row, 1, QTableWidgetItem(player))
        self.chat_table.setItem(row, 2, QTableWidgetItem(message))

    def add_join_row(self, player, action):
        if not self.join_table:
            return
        row = self.join_table.rowCount()
        self.join_table.insertRow(row)
        self.join_table.setItem(row, 0, QTableWidgetItem(timestamp()))
        self.join_table.setItem(row, 1, QTableWidgetItem(player))
        self.join_table.setItem(row, 2, QTableWidgetItem(action))

    def launch_and_watch(self):
        try:
            proc = subprocess.Popen(
                ["flatpak", "run", "org.vinegarhq.Sober"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            for line in proc.stdout:
                line = line.strip()
                if not line:
                    continue

                if "Incoming MessageReceived" in line:
                    msg = chat_pattern.search(line)
                    player_match = chat_player_pattern.search(line)
                    if msg:
                        if player_match:
                            userid, text = player_match.groups()
                            name = self.players.get(userid, f"unknown ({userid})")
                            self.add_chat_row(name, text)
                        else:
                            self.add_chat_row("unknown", msg.group(1))

                elif "Player added" in line or "Player removed" in line:
                    player = player_pattern.search(line)
                    if player:
                        action, name, userid = player.groups()
                        if action == "added":
                            self.players[userid] = name
                        elif action == "removed":
                            self.players.pop(userid, None)
                        self.add_join_row(name, f"{action} ({userid})")

        except Exception as e:
            print(f"[error] {e}")
        finally:
            proc.terminate()
            self.finished_signal.emit()


def main():
    app = QApplication(sys.argv)
    main_app = MainApp()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
