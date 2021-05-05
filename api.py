import json
import requests
class API:
    foundUUIDs = {}
    foundPlayers = {}
    
    # TODO: Queue party and self for statistics refresh when requested

    def __init__(self):
        self.foundPlayers.setdefault(-1)
        self.foundUUIDs.setdefault(-1)

    def hypixel(self, token, uuid):
        if (uuid in self.foundUUIDs):
            return self.foundUUIDs[uuid]
        player = requests.get("https://api.hypixel.net/player?key={}&uuid={}".format(token, uuid)).content
        self.foundUUIDs[uuid] = player
        return player

    def minecraft(self, username):
        if (username in self.foundPlayers):
            return self.foundPlayers[username]
        uuid = json.loads(requests.get("https://api.mojang.com/users/profiles/minecraft/" + username).content)["id"]
        self.foundPlayers[username] = uuid
        return uuid