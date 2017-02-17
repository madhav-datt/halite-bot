import urllib
import requests
from time import sleep
import numpy as np
import wget
import os.path
import pickle

### Download user ids
"""
request = u"https://halite.io/api/web/user?fields%5B%5D=isRunning&values%5B%5D=1&orderBy=rank&limit=1000&page=0"

r = requests.get(request)
users = r.json()["users"]
user_ids = [user['userID'] for user in users]


### Download games from one user

user = "2609"
request = "https://halite.io/api/web/game?userID={}&limit=1000".format(user)
r = requests.get(request)
game_ids = [game['replayName'] for game in r.json()]

with open(r"ids.pkl", "wb") as output_file:
    pickle.dump(game_ids, output_file)
"""

with open(r"ids.pkl", "rb") as input_file:
    game_ids = pickle.load(input_file)


# testfile = urllib.request.URLopener()
print("starting")
for game_id in game_ids:
    if os.path.isfile(game_id):
        continue
    request = "https://s3.amazonaws.com/halitereplaybucket/{}".format(game_id)
    # r = requests.get(request)
    wget.download(request)
    print(game_id)
    # testfile.retrieve(request, "{}.gzip".format(game_id))
    sleep(np.random.rand())
