from pathlib import Path

from tomlkit import TOMLDocument, dumps, loads, table


class Config:
    def __init__(self, config_path="LutionConfig.toml"):
        self.config_path = Path(config_path)

        if not self.config_path.exists():
            self.config_path.write_text("", encoding="utf-8")

        self.configdata = self._load()

    def _load(self):
        text = self.config_path.read_text(encoding="utf-8").strip()
        if not text:
            return TOMLDocument()
        return loads(text)

    def reload(self):
        self.configdata = self._load()

    def add_row(self, table_name: str, row: str, value):
        if table_name not in self.configdata:
            self.configdata[table_name] = table()
        self.configdata[table_name][row] = value

    def get_row(self, table_name: str, row: str, default=None):
        return self.configdata.get(table_name, {}).get(row, default)

    def get_table(self, table_name: str):
        return self.configdata.get(table_name)

    def remove_row(self, table_name: str, row: str):
        if table_name in self.configdata:
            self.configdata[table_name].pop(row, None)

    def save(self):
        self.config_path.write_text(dumps(self.configdata), encoding="utf-8")
