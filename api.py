from typing import ClassVar
import json
import requests
hypixelUrl = "https://api.hypixel.net/"
minecraftUrl = "https://api.mojang.com/"
class API:
    def hypixel(self, token, uuid):
        if (not self.checkup()):
            return -1
        return requests.get(hypixelUrl + "player?key={}&uuid={}".format(token, uuid)).content

    def minecraft(self, username):
        if (not self.checkup()):
            return -1
        return json.loads(requests.get(minecraftUrl + "users/profiles/minecraft/" + username).content)["id"]
        
    def checkup(self):
        hypixel = requests.get(hypixelUrl)
        minecraft = requests.get(minecraftUrl)
        if (not hypixel):
            print("Hypixel API server seems to be down")
            return False
        if (not minecraft):
            print("Minecraft API server seems to be down")
            return False
        return True
        
