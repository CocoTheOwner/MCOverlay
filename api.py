import time, json, requests
from Config import Config
from json.decoder import JSONDecodeError
from concurrent.futures import ThreadPoolExecutor, as_completed
from fake_useragent import UserAgent

ua = UserAgent()
"""Module for retrieving data from several preset API pages"""
class API:
    token = ""
    debug = False

    uuidsFile = Config("./cache/uuids.json", {})
    uuids = uuidsFile.config
    uuidsFile.load()

    stats = {}

    # TODO: Queue party and self for statistics refresh when requested

    def __init__(self, token: str, debug = False):
        self.token = token
        self.debug = debug

    def fetch(self, playerQueue):
        """Fetches all player data from a queue

        Args:
            playerQueue (dict): Queue of players to get stats of

        """
        if not self.getRequest("https://api.mojang.com/")["Status"] == "OK":
            print("Minecraft API is down!")
            return
        threads = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            count = 0
            total = len(playerQueue)
            for player in playerQueue:
                count += 1
                threads.append(executor.submit(self.getPlayerData, player))

            for task in as_completed(threads):
                if self.debug and (total-count)%10==0: print("Completed task ({}/{}) | Result: {}".format(total - count, total, str(len(task.result()))))
                count -= 1
                
            executor.shutdown(True)
        self.uuidsFile.save()

    def getPlayerData(self, player):
        """Retrieves player data of a player
        
        Args:
            player (str): Playername
            file (Config): Configuration file to write results to and take existing results from

        """
        try:

            # Get UUID from minecraft's API
            uuid = self.minecraft(player)
            if uuid == None: return "NoneUUID"
            if uuid == "NICK": return "NICK"
            self.uuidsFile.set(player, uuid)

            # Get Stats from hypixel's API
            stats = self.hypixel(player, uuid)
            if stats == None: return None
            self.stats[uuid] = stats

            # Return the statistics
            return stats

        except requests.exceptions.RequestException as e:
            print("Failed player fetch for " + player)
            raise e
        except Exception as e:
            print("An unhandled exception was raised for player: {}\nError: {}".format(player, str(type(e))))
            raise e

    def hypixel_stats(self):
        """Retrieve hypixel API server information

        Returns:
            None if failed, record with information if successful
        """
        request = self.getRequest("https://api.hypixel.net/key?key={}".format(self.token))
        if request == None or request["success"] != "true":
            return None
        else:
            return request["record"]

    def hypixel(self, player, uuid):
        """Retrieves stats of player with uuid

        Args:
            player (str): Name of the player
            uuid (str): UUID of the player

        Returns:
            None if failed, dict with data if successful
        """
        if self.debug: print("Downloading stats of {} ({})".format(player, uuid))
        request = self.getRequest("https://api.hypixel.net/player?key={}&uuid={}".format(self.token, uuid))
        if request != None and "player" in request:
            if self.debug: print(player + "'s stats download successful")
            self.stats[uuid] = request["player"]
            return request["player"]
        elif self.debug and request != None:
            print("Error when getting Stats for {}: {}".format(player, request["cause"] if request != None and "cause" in request else ("Request is 'None'" if request == "None" else request)))

    def minecraft(self, username):
        """Retrieves UUID of a player

        Args:
            username (str): Username of the player to get data from

        Returns:
            UUID string

        """
        # Prevent loading same username twice
        if username in self.uuids:
            return self.uuids[username]
        
        # Get UUID from server
        #if self.debug: print("Downloading UUID of {}".format(username))
        request = self.getRequest("https://api.mojang.com/users/profiles/minecraft/" + username)
        if request != None and not 'error' in request:
            self.uuids[username] = request["id"]
            return request["id"] 
        else:
            self.uuids[username] = "NICK"
            return "NICK"

    def getRequest(self, link):
        """Retrieves request from webpage

        Args:
            link (str): Link to query

        Returns:
            None if failed, content of webpage get if successful
        
        """
        request = requests.get(link, headers={'User-Agent':str(ua.random), "Connection": "close"}).content
        try:
            return json.loads(request)
        except JSONDecodeError as e:
            if self.debug: print("Failed to request from {} because of JSON Decode Error. Likely due to invalid link or no connection.\nLink: {}\nReturned: {}".format(e, link, request))