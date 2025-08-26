import requests
import json


class contributors():
    def __init__(self):
        self.contributors = []

    def get_contributors(self):
        response = requests.get("https://api.github.com/repos/Wookhq/Lution/contributors")

        if response.status_code == 200:
            self.contributors = [
                c for c in response.json()
                if c.get("login") not in ["crowdin-bot"]
            ]
            return self.contributors
        else:
            print(f"Error: {response.status_code}")
            return None
        
    def get_bio(self, username):
        response = requests.get(f"https://api.github.com/users/{username}")

        if response.status_code == 200:
            return response.json().get("bio", "")
        else:
            print(f"Error: {response.status_code}")
            return None
            
