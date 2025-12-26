# trust we will not send your cookie to evil scary larry corperation
# i just gonna explain what this do cuz if you are not a dev you'll think this is sus

import json
import os

import requests


def getCookie():  # trust
    from modules.config import Config

    cfg = Config()

    sb = cfg.get_row("Sober", "Path")
    cookies = os.path.expanduser(f"{sb}/data/sober/cookies")  # get the cookie path

    with open(cookies, "r") as c:  # open it
        data = c.read()  # read it
        c.close()
        cookies = data.split(";")  # dict it
        cookie_dict = {}

        for c in cookies:
            if "=" in c:
                k, v = c.strip().split("=", 1)
                cookie_dict[k] = v

    return cookie_dict  # then return the dict


def getName(cookies: dict):  # trust the process
    r = requests.get(
        "https://users.roblox.com/v1/users/authenticated", cookies=cookies
    )  # fetching roblox's offical api for display name
    r.raise_for_status()
    data = r.json()
    return data.get("displayName", "User")  # return name
