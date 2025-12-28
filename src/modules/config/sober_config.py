import json
import os

from jsonc_parser.parser import JsoncParser

from modules.config import Config


class SoberConfig:
    def __init__(self) -> None:
        self.cfg = Config()
        self.configpath = os.path.expanduser(
            f"{self.cfg.get_row('Sober', 'Path')}/config/sober/config.json"
        )
        self.data = JsoncParser.parse_file(self.configpath)

    def read_key(self, key):
        return self.data[key]

    def write_key(self, key, value):
        self.data[key] = value
        self._save()

    def _save(self):
        jsonstr = json.dumps(self.data, indent=4)
        with open(
            self.configpath,
            "w",
        ) as f:
            f.write(jsonstr)
