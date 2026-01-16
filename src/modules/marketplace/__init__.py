import json
import os
from pathlib import Path

import requests
from github import Auth, Github

from modules.config import Config


class MarketplaceItemNotFound(Exception):
    pass


class MarketplaceInvaildData(Exception):
    pass


class MarketplaceHelper:
    def __init__(self):
        self.cfg = Config()
        api_key = self.cfg.get_row("Lution", "GithubKeyAPI")
        self.repo_name = self.cfg.get_row("Lution", "MarketplaceRepo")

        if not api_key or api_key == "None":
            self.g = Github()
        else:
            auth = Auth.Token(api_key)
            self.g = Github(auth=auth)

        self.repo = self.g.get_repo(self.repo_name)

        self.download_dir = os.path.expanduser(
            self.cfg.get_row("Lution", "MarketplaceFiles")
        )

    def list_items(self):
        content_file = self.repo.get_contents("src/index.json")
        decoded = content_file.decoded_content.decode("utf-8")
        return json.loads(decoded)

    # https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
    def _download_file(self, url, location):
        location = Path(location)
        location.mkdir(parents=True, exist_ok=True)

        filename = Path(url).name
        file_path = location / filename

        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        return file_path

    def download_item(self, id):
        print("DEBUG : checking all ids from remote")
        data = self.list_items()

        print("DEBUG : finding")

        mods = data.get("Mods", [])

        result = next((item for item in mods if item.get("id") == id), None)

        if result is None:
            print("DEBUG : Not found")
            raise MarketplaceItemNotFound

        print("DEBUG : Found:", result)
        print("DEBUG : Downloading that...")

        if not result.get("asset"):
            raise MarketplaceInvaildData

        self._download_file(
            f"https://github.com/{self.repo_name}/raw/refs/heads/main/src/{result['asset']}?download=",
            self.download_dir,
        )

        print("DEBUG : done!!")
