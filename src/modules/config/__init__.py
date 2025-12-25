from pathlib import Path

from tomlkit import dumps, loads, table


class Config:
    def __init__(self, config_path="LutionConfig.toml"):
        self.config_path = Path(config_path)

        if not self.config_path.exists():
            self.config_path.write_text("", encoding="utf-8")

        self.configdata = loads(self.config_path.read_text(encoding="utf-8"))

    def add_row(self, table_name: str, row: str, value):
        if table_name not in self.configdata:
            self.configdata[table_name] = table()

        self.configdata[table_name][row] = value

    def get_row(self, table_name: str, row: str, default=None):
        return self.configdata.get(table_name, {}).get(row, default)

    def get_table(self, table_name: str):
        return self.configdata.get(table_name)

    def reload(self):
        self.configdata = loads(self.config_path.read_text(encoding="utf-8"))

    def remove_row(self, table_name: str, row: str):
        self.configdata.get(table_name, {}).pop(row, None)

    def save(self):
        self.config_path.write_text(dumps(self.configdata), encoding="utf-8")

    def initConfig(self):
        if not self.get_row("Lution", "FirstTimeLaunch"):
            self.add_row("Lution", "language", "en_US")
            self.add_row("LutionSplash", "CurrentSplash", "Default")
            self.add_row(
                "LutionSplash", "Splashs", ["Default", "Calling"]
            )  # hard coded for now
            self.add_row("Lution", "FirstTimeLaunch", "False")
            self.add_row("Sober", "Path", "~/.var/app/org.vinegarhq.Sober")
            self.save()
        else:
            return
