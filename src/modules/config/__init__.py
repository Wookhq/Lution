import os
from pathlib import Path

from tomlkit import TOMLDocument, dumps, loads, table

CONFIG_APP_NAME = "Chroma"
CONFIG_FILE_NAME = "LutionConfig.toml"

config_home = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
config_dir = config_home / CONFIG_APP_NAME
config_dir.mkdir(parents=True, exist_ok=True)

config_file = config_dir / CONFIG_FILE_NAME


class Config:
    def __init__(self, config_path: Path | None = None):
        self.config_path = Path(config_path) if config_path else config_file

        if not self.config_path.exists():
            self.config_path.write_text("", encoding="utf-8")

        self.configdata = self._load()

    def _load(self) -> TOMLDocument:
        text = self.config_path.read_text(encoding="utf-8").strip()
        if not text:
            return TOMLDocument()
        return loads(text)

    def reload(self) -> None:
        self.configdata = self._load()

    def save(self) -> None:
        self.config_path.write_text(
            dumps(self.configdata),
            encoding="utf-8",
        )

    def add_row(
        self,
        table_name: str,
        row: str,
        value,
        *,
        autosave: bool = False,
    ) -> None:
        if table_name not in self.configdata:
            self.configdata[table_name] = table()

        self.configdata[table_name][row] = value

        if autosave:
            self.save()

    def get_row(self, table_name: str, row: str, default=None):
        return self.configdata.get(table_name, {}).get(row, default)

    def get_table(self, table_name: str):
        return self.configdata.get(table_name)

    def remove_row(
        self,
        table_name: str,
        row: str,
        *,
        autosave: bool = False,
    ) -> None:
        if table_name in self.configdata:
            self.configdata[table_name].pop(row, None)

            if autosave:
                self.save()
