import json
from json.decoder import JSONDecodeError
import requests
class API:
    foundUUIDs = {}
    foundPlayers = {}
    
    # TODO: Queue party and self for statistics refresh when requested

    def __init__(self, foundPlayers: dict, foundUUIDs: dict):
        self.foundPlayers = foundPlayers
        self.foundUUIDs = foundUUIDs

    def hypixel(self, token, uuid):
        if (uuid in self.foundUUIDs):
            return self.foundUUIDs[uuid]
        player = requests.get("https://api.hypixel.net/player?key={}&uuid={}".format(token, uuid)).content
        self.foundUUIDs[uuid] = player
        return player

    def minecraft(self, username):
        if (username in self.foundPlayers):
            return self.foundPlayers[username]
        print("Getting UUID of {}".format(username))
        request = ""
        uuid = -1
        try:
            request = requests.get("https://api.mojang.com/users/profiles/minecraft/" + username).content
            uuid = json.loads(request)["id"]
        except JSONDecodeError:
            print("Failed to load json from {}.\n{}".format("https://api.mojang.com/users/profiles/minecraft/" + username, str(request)))
        self.foundPlayers[username] = uuid
        return uuid