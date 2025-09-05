import sys
import json
import os
from modules.mod.clientsettings import ClientSettings
from modules.config.genconfig import Config
from PySide6.QtWidgets import QApplication, QDialog, QTableWidgetItem
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

client_settings = ClientSettings()
cg = Config()

class JsonDialog(QDialog):
    def __init__(self, data, ui_file):
        super().__init__()

        # config vars
        spilted = client_settings.SplitClientSettingsContent()
        self.currfflags = json.loads(spilted or "{}")

        # load .ui
        loader = QUiLoader()
        ui_file_obj = QFile(ui_file)
        ui_file_obj.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file_obj, self)
        ui_file_obj.close()

        self.setLayout(self.ui.layout())

        # table inside .ui
        self.table = self.findChild(type(self.ui.tableWidget), "tableWidget")
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["key", "value"])

        # connection
        self.findChild(type(self.ui.buttonBox), "buttonBox").accepted.connect(self.save_and_close)

        # if filename given, load it
        if isinstance(data, (str, bytes)):
            with open(data, "r") as f:
                data = json.load(f)

        # fill table
        rows = [(k, str(v)) for k, v in data.items()]
        self.table.setRowCount(len(rows))
        for i, (k, v) in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(k))
            self.table.setItem(i, 1, QTableWidgetItem(v))


    def save_and_close(self):
        valuetable = self.table_to_dict()
        res = cg.CombineJson(valuetable, self.currfflags)
        cg.UpdateSoberConfig("fflags", valuetable)


    def table_to_dict(self):
        data = {}
        for row in range(self.table.rowCount()):
            key_item = self.table.item(row, 0)
            val_item = self.table.item(row, 1)

            if key_item is not None:
                key = key_item.text()
                value = val_item.text() if val_item else ""
                data[key] = value
        return data

def run():
    spilted = client_settings.SplitClientSettingsContent()
    Currfflags = json.loads(spilted or "{}")

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    base = os.path.dirname(__file__)
    uifl = os.path.join(base, "..", "files", "advanced_editor.ui")

    dialog = JsonDialog(Currfflags, ui_file=uifl)
    dialog.exec()   # modal popup
