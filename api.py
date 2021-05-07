import json
from json.decoder import JSONDecodeError
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from requests.api import request
class API:
    players = {}
    token = ""

    # TODO: Queue party and self for statistics refresh when requested

    def __init__(self, players: dict, token: str):
        self.players = players
        self.token = token

    def fetch(self, playerQueue, file):
        threads = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            count = 0
            total = len(playerQueue)
            for player in playerQueue:
                count += 1
                threads.append(executor.submit(self.getPlayerData, player, file))

            for task in as_completed(threads):
                print("Completed task ({}/{}) | Result: {}".format(total - count, total, str(task.result())))
                count -= 1

    def getPlayerData(self, player, file):
        try:
            uuid = self.minecraft(player)
            file.set(player, uuid)
            if (uuid == None): return None
            stats = self.hypixel(player, uuid)
            file.set(uuid, stats)
            return stats
        except requests.exceptions.RequestException as e:
            print("Failed player fetch for " + player)
            return e
        finally:
            print("Completed data retrieval for " + player)

    def hypixel_stats(self):
        request = API.getRequest("https://api.hypixel.net/key?key={}".format(self.token))
        if request == None or request["success"] != "true":
            return None
        else:
            return request["record"]

    def hypixel(self, player, uuid):
        print("Downloading stats of {} ({})".format(player, uuid))
        request = API.getRequest("https://api.hypixel.net/player?key={}&uuid={}".format(self.token, uuid))
        if request == None or request["success"] != "true":
            self.players[uuid] = None
        else:
            self.players[uuid] = request["player"]
        return request["player"]

    def minecraft(self, username):

        # Prevent loading same username twice
        if (username in self.players):
            if type(self.players[username]) == str:
                return self.players[username]
            elif type(self.players[username]) == dict:
                return self.players[username]["uuid"]
        
        # Get UUID from server
        print("Downloading UUID of {}".format(username))
        request = API.getRequest("https://api.mojang.com/users/profiles/minecraft/" + username)
        return request["id"] if request != None else -1

    def getRequest(link):
        content = None

        try:
            content = json.loads(requests.get(link, headers={'Connection': 'close'}).content)
        except JSONDecodeError as e:
            print("Failed to request from {} because of JSON Decode Error. Likely due to invalid link or no connection.".format(e))
        except Exception as e:
            print("Failed to request from {} because of an Exception:\n{}".format(link, e))

        return content