import json
from github import Github, Auth
from modules.config import Config

cfg = Config()

class MarketplaceHelper:
    def __init__(self):
        api_key = cfg.get_row("Lution", "GithubKeyAPI")
        repo_name = cfg.get_row("Lution", "MarketplaceRepo")

        if not api_key or api_key == "None":
            self.g = Github()
        else:
            auth = Auth.Token(api_key)
            self.g = Github(auth=auth)

        self.repo = self.g.get_repo(repo_name)

    def list_items(self):
        content_file = self.repo.get_contents("src/index.json")
        decoded = content_file.decoded_content.decode("utf-8")
        return json.loads(decoded)
