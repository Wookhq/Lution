from github import Github as auth
from modules.utils.files import FilesFunctions
from modules.config.genconfig import Config
import os
import zipfile
import json
import time
import base64
import shutil

cf = Config()
ff = FilesFunctions()

authtoken = cf.Read("marketplace", "githubtoken")

if authtoken is None:   
    g = auth()
else:
    g = auth(authtoken)
    
class MarketplaceManager:
    def __init__(self, github_obj):
        self.g = github_obj

    def Unzip(self, zip_file_path, extract_to_path):
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to_path)
            print(f"Successfully extracted '{zip_file_path}' to '{extract_to_path}'")
        except FileNotFoundError:
            print(f"Error: The file '{zip_file_path}' was not found.")
        except zipfile.BadZipFile:
            print(f"Error: The file '{zip_file_path}' is not a valid ZIP file.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def GHFiles(self, repo_name, file_path, output_path, max_retries=3, retry_delay=5):
        repo = self.g.get_repo(repo_name)
        for attempt in range(max_retries):
            try:
                print(f"Attempting to download '{file_path}' from '{repo_name}' (Attempt {attempt + 1}/{max_retries})")
                file_content = repo.get_contents(file_path)
                if file_content.encoding == 'base64':
                    content = base64.b64decode(file_content.content)
                else:
                    content = file_content.decoded_content

                try:
                    print(f"[debug] output_path: {output_path}")
                    print(f"[debug] parent dir exists: {os.path.exists(os.path.dirname(output_path))}")
                    print(f"[debug] parent dir writable: {os.access(os.path.dirname(output_path), os.W_OK)}")
                    print(f"[debug] file size to write: {len(content)} bytes")
                    
                    with open(output_path, "wb") as f:
                        f.write(content)
                    print(f"Successfully downloaded '{file_path}' from '{repo_name}' to '{output_path}'")
                    return
                except OSError as e:
                    print(f"OS error occurred: {e}")
                    raise

            except Exception as e:
                print(f"Download failed (Attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("Max retries reached. Download failed.")
                    raise

    def downloaditems(self, Name, type, installedlist):
        curf = cf.Read("marketplace", installedlist)
        if not curf:
            curf = ""
        if Name not in curf:
            cf.Update("marketplace", installedlist, Name + "," + curf if curf else Name)

        repo_name = cf.Read("marketplace", "marketplaceprd")
        repo = self.g.get_repo(repo_name)
        download_dir = os.path.expanduser(f"~/Documents/Lution/Lution Marketplace/{type}s/{Name}")
        os.makedirs(download_dir, exist_ok=True)

        if type == "theme":
            info_file_path = "Assets/Themes/info.json"
        elif type == "mod":
            info_file_path = "Assets/Mods/info.json"
        else:
            print(f"Unknown type '{type}'")
            return None

        content = repo.get_contents(info_file_path)
        info_list = json.loads(content.decoded_content.decode())
        entry = next((item for item in info_list if item["name"] == Name), None)

        if entry:
            zip_path = entry["path"]
            local_zip_path = os.path.join(download_dir, os.path.basename(zip_path))
            self.GHFiles(repo_name, zip_path, local_zip_path)

            if zipfile.is_zipfile(local_zip_path):
                self.Unzip(local_zip_path, download_dir)
                os.remove(local_zip_path)
                return download_dir
            else:
                print(f"Error: {local_zip_path} is not a valid zip file.")
        else:
            print(f"No {type} found with name '{Name}'")
        return None

    def DownloadMarketplace(self, Name, type):
        if type == "theme":
            return self.downloaditems(Name, type, "InstalledThemes")
        elif type == "mod":
            return self.downloaditems(Name, type, "InstalledMods")
        return None

    def RemoveMarketplace(self, Name, Type):
        print("funtion called")
        path = os.path.expanduser(f"~/Documents/Lution/Lution Marketplace/{Type}s/{Name}")
        if Type == "mod":
            cf.RemoveValueFromList("marketplace", "InstalledMods", Name)
            if os.path.isdir(path):
                shutil.rmtree(path)
        if Type == "theme":
            cf.RemoveValueFromList("marketplace", "InstalledThemes", Name)
            if os.path.isdir(path):
                shutil.rmtree(path)

    def ApplyMarketplace(self, Name, type):
        ff.ResetMods2()
        download_dir = os.path.expanduser(f"~/Documents/Lution/Lution Marketplace/{type}s/{Name}")
        ff.ApplyMarketplaceMods(download_dir)
   
    def get_fastflag_content(self, repo_name, file_path):
        repo = self.g.get_repo(repo_name)
        file_content = repo.get_contents(file_path)
        if file_content.encoding == 'base64':
            content = base64.b64decode(file_content.content)
        else:
            content = file_content.decoded_content
        return content