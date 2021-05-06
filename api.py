import json
from json.decoder import JSONDecodeError
import requests
class API:
    players = {}
    
    # TODO: Queue party and self for statistics refresh when requested

    def __init__(self, players: dict,):
        self.players = players

    def hypixel(self, token, uuid):
        if (uuid in self.players and self.players[uuid] is dict):
            return self.players[uuid]
        request = ""
        try:
            request = requests.get("https://api.hypixel.net/player?key={}&uuid={}".format(token, uuid)).content
            self.players[uuid] = json.loads(request)
        except Exception:
            print("Failed to retrieve or load json for {} ({}), got: {}".format(uuid, self.players[uuid], request))
        return request

    def minecraft(self, username):
        if (username in self.players):
            return (self.players[username] if type(self.players[username]) == str else self.players[username]["uuid"])
        print("Downloading UUID of {}".format(username))
        request = ""
        uuid = -1
        try:
            request = requests.get("https://api.mojang.com/users/profiles/minecraft/" + username).content
            uuid = json.loads(request)["id"]
        except JSONDecodeError:
            print("Failed to load json from {}.\n{}".format("https://api.mojang.com/users/profiles/minecraft/" + username, str(request)))
        self.players[username] = uuid
        return uuid