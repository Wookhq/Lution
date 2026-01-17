# trust we will not send your cookie to evil scary larry corperation
# i just gonna explain what this do cuz if you are not a dev you'll think this is sus

import json
import os
import re

import requests

from modules.config import Config # to chip: just why

cfg = Config()

# def getCookie():  # trust
#     sb = cfg.get_row("Sober", "Path")
#     cookies = os.path.expanduser(f"{sb}/data/sober/cookies")  # get the cookie path

#     with open(cookies, "r") as c:  # open it
#         data = c.read()  # read it
#         c.close()
#         cookies = data.split(";")  # dict it
#         cookie_dict = {}

#         for c in cookies:
#             if "=" in c:
#                 k, v = c.strip().split("=", 1)
#                 cookie_dict[k] = v

#     return cookie_dict  # then return the dict

def getUserIdFromLogs():
    sb = cfg.get_row("Sober", "Path")
    logsPath = os.path.expanduser(f"{sb}/data/sober/sober_logs")
    logFiles = sorted(
        [os.path.join(logsPath, i) for i in os.listdir(logsPath)],
        key = os.path.getmtime,
        reverse = True
    )
    for logFile in logFiles:
        with open(logFile) as logFileIO:
            print(f"Searching {logFile} for user id")
            for line in logFileIO:
                if "[FLog::GameJoinLoadTime] Report game_join_loadtime:" in line:
                    userid = re.search(
                        r"userid:(\d+)",
                        line
                    )
                    if not userid:
                        print(f"Couldn't find user id from this line: {line}")
                    userid = int(userid.group(1))
                    print(f"Retrieved user id: {userid}")
                    return userid
        print(f"{logFile} doesn't contain any logs related to joining a game. Searching next log file")
    print(f"Couldn't find user id, returning None!")
    return

# def getName(cookies: dict):  # trust the process
#     r = requests.get(
#         "https://users.roblox.com/v1/users/authenticated", cookies=cookies
#     )  # fetching roblox's offical api for display name
#     r.raise_for_status()
#     data = r.json()
#     return data.get("displayName", "User")  # return name

def getName(userId: int):
    r = requests.get(f"https://users.roblox.com/v1/users/{userId}")
    r.raise_for_status()
    data = r.json()
    return data.get("displayName", "User")