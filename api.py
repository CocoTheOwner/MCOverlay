import time, json, requests
from Config import Config
from json.decoder import JSONDecodeError
from concurrent.futures import ThreadPoolExecutor, as_completed
from fake_useragent import UserAgent
import traceback

ua = UserAgent()
"""Module for retrieving data from several preset API pages"""
class API:
    token = ""
    debug = False

    uuidsFile = Config("./cache/uuids.json", {})
    uuids = uuidsFile.config
    uuidsFile.hotload()

    stats = {}

    # These store an array of timestamps. The length is the amount of requests.
    MCAPIRequests = []
    MCAPIRequestsMax = 600 # Per 10 minutes.
    HYAPIRequests = []
    HYAPIRequestsMax = 120 # Per minute.

    def __init__(self, token: str, debug = False):
        self.token = token
        self.debug = debug

    def fetch(self, playerQueue):
        """Fetches all player data from a queue

        Args:
            playerQueue (dict): Queue of players to get stats of

        """
        failed = 0
        maxFailed = 60
        while failed < maxFailed:
            MCAPI = self.getRequest("https://api.mojang.com/")
            if MCAPI == None or MCAPI["Status"] != "OK":
                self.file("MC", "API is down!")
                failed += 1
                time.sleep(2)
            else:
                break
        if failed == maxFailed:
            self.file("MC", "API has been down for 2 minutes. Fetch failed!")
            return
        if failed > 0:
            self.file("MC", "API has been down for {} seconds, but has resumed work.".format(str(failed * 2)))
        if self.debug: self.file("REQ", "Fetching statistics for: " + ", ".join(playerQueue), False)
        threads = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            count = 0
            total = len(playerQueue)
            for player in playerQueue:
                count += 1
                threads.append(executor.submit(self.getPlayerData, player))

            for task in as_completed(threads):
                if self.debug and (total-count)%10==0: self.file("REQ", "Completed task ({}/{}) | Result: {}".format(total - count, total, str(len(task.result()))), False)
                count -= 1
                
            executor.shutdown(True)
        self.uuidsFile.save()

    def getPlayerData(self, player: str):
        """Retrieves player data of a player
        
        Args:
            player (str): Playername
            file (Config): Configuration file to write results to and take existing results from

        """
        uuid = None
        stats = None
        try:
            # Lowercase playername
            player = player.lower()

            # Get UUID from minecraft's API
            uuid = self.minecraft(player)
            if uuid == None: return "NoneUUID"
            if uuid == "NICK": return "NICK"
            self.uuidsFile.set(player, uuid)

            # Get Stats from hypixel's API
            stats = self.hypixel(player, uuid)
            if stats == None: return "NoStats"
            self.stats[uuid] = stats

            # Prevent request throttle
            time.sleep(0.4)

            # Return the statistics
            return stats

        except requests.exceptions.RequestException as e:
            self.file("REQ", "Failed player fetch for " + player)
            raise e
        except TypeError:
            self.file("REQ", "Likely one of the responses failed. UUID: {}, Stats: {}".format(uuid, "None" if stats==None else stats[:100]))
        except Exception as e:
            self.file("REQ", "An unhandled exception was raised for player: {}\nError: {}".format(player, str(type(e))))
            self.file("REQ", "Trackeback: {}".format(traceback.format_exc()))
            raise e

    def printHypixelStats(self):
        """Retrieve hypixel API server information

        Returns:
            ONLINE (bool): True if online, false if not
        """
        start = time.time()
        if self.updateHYAPIRequests():
            self.HYAPIRequests.append(start)
            request = self.getRequest("https://api.hypixel.net/key?key={}".format(self.token))
            if request == None:
                self.file("HY", "OFFLINE (no response, took {}s)".format(round(time.time() - start,1)))
            elif request["success"] != True:
                self.file("HY", "UNRESPONSIVE (response not successful: {}, took {}s)".format(request, round(time.time() - start,1)))
            else:
                if len(self.HYAPIRequests) - 1 != request["record"]["queriesInPastMin"]:
                    self.file("HY", "May overflow. Correcting. (MCO's count: {}, Hypixel's count: {})".format(len(self.HYAPIRequests), request["record"]["queriesInPastMin"]), False)
                    for _ in range(0, len(self.HYAPIRequests) - 1 - request["record"]["queriesInPastMin"]):
                        self.HYAPIRequests.pop()
                    for _ in range(0, request["record"]["queriesInPastMin"] - len(self.HYAPIRequests) + 1):
                        self.HYAPIRequests.append(time.time())
                if self.HYAPIRequestsMax != request["record"]["limit"]:
                    self.file("HY", "Cap is incorrect on our end. Correcting. Our cap: {}, Hypixel's cap: {}".format(self.HYAPIRequestsMax, request["record"]["limit"]), False)
                    self.HYAPIRequestsMax = request["record"]["limit"]
                self.file("HY", "ONLINE (requests: {}/{} per 60s. {} in total. Took {}s)".format(len(self.HYAPIRequests), self.HYAPIRequestsMax, request["record"]["totalQueries"], round(time.time() - start,1)), False)
                return True
        else:
            self.file("HY", "Could not download API usage for because the API is overloaded: {}/{}".format(len(self.HYAPIRequests), self.HYAPIRequestsMax))
        return False
            

    def hypixel(self, player, uuid):
        """Retrieves stats of player with uuid

        Args:
            player (str): Name of the player
            uuid (str): UUID of the player

        Returns:
            None if failed, dict with data if successful
        """
        if self.updateHYAPIRequests():
            self.HYAPIRequests.append(time.time())
            if self.debug: self.file("REQ", "Downloading stats of {} ({})".format(player, uuid), False)
            request = self.getRequest("https://api.hypixel.net/player?key={}&uuid={}".format(self.token, uuid))
            if request != None and "player" in request:
                if self.debug: self.file("REQ", player + "'s stats download successful", False)
                self.stats[uuid] = request["player"]
                if self.debug: self.verifyPlayername(player, uuid, request["player"]["playername"], request["player"]["uuid"])
                if self.debug: self.file("HY", "Successfully retrieved statistics.", False)
                return request["player"]
            elif self.debug and request != None:
                self.file("HY", "Error when getting Stats for {}: {}".format(player, request["cause"] if request != None and "cause" in request else ("Request is 'None'" if request == "None" else request)))
        else:
            self.file("HY", "Could not download stats for {} ({}) because the API is overloaded: {}/{}".format(player, uuid, len(self.HYAPIRequests), self.HYAPIRequestsMax))
            self.file("HY", "Warning, this player is completely ignored and will not show up on your statistics list!")
            return None

    def printMinecraftStats(self):
        """Retrieves stats of minecraft API

        Returns:
            ONLINE (bool): True if online, False if not
        """
        start = time.time()
        if self.updateMCAPIRequests():
            self.MCAPIRequests.append(time.time())
            request = self.getRequest("https://api.mojang.com/")
            if request == None:
                self.file("MC", "OFFLINE (no response, took {}s)".format(round(time.time() - start,1)), False)
                return False
            else:
                self.file("MC", "ONLINE (version: {}, {}/{} requests per 600s. Took {}s)".format(request["Implementation-Version"], len(self.MCAPIRequests), self.MCAPIRequestsMax, round(time.time() - start,1)), False)
                return True
        else:
            self.file("MC", "Could not download API usage for because the API is overloaded: {}/{}".format(len(self.MCAPIRequests), self.MCAPIRequestsMax), False)

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
        
        if self.updateMCAPIRequests():
            self.MCAPIRequests.append(time.time())
            # Get UUID from server
            request = self.getRequest("https://api.mojang.com/users/profiles/minecraft/" + username)
            if request != None and not 'error' in request:
                self.uuids[username] = request["id"]
                return request["id"] 
            else:
                self.uuids[username] = "NICK"
                return "NICK"
        else:
            self.file("MC", "Could not download uuid for {} because the API is overloaded: {}/{}".format(username, len(self.MCAPIRequests), self.MCAPIRequestsMax))
            self.file("MC", "WARN: This player is completely ignored and will not show up on your statistics list!")
            return None

    def updateHYAPIRequests(self):
        now = time.time()
        for timeStamp in self.HYAPIRequests:
            if now - timeStamp > 60:
                self.HYAPIRequests.remove(timeStamp)
        return self.HYAPIRequestsMax > len(self.HYAPIRequests)

    def updateMCAPIRequests(self):
        now = time.time()
        for timeStamp in self.MCAPIRequests:
            if now - timeStamp > 600:
                self.MCAPIRequests.remove(timeStamp)
        return self.MCAPIRequestsMax > len(self.MCAPIRequests)

    def verifyPlayername(self, name1, uuid1, name2, uuid2):
        if name1 not in self.uuids:
            self.file("HY", "UUID of player entered is somehow not in our list. This should never occur, if it does, something is very broken: {}".format(name1))
        elif name2 not in self.uuids:
            self.file("HY", "UUID of playername returned not in our list. Likely due to namechange: {}".format(name2))
        elif name1 != name2:
            if uuid1 != uuid2:
                self.file("HY", "UUID of playername returned not in our log: Lookup {} / Hypixel {} ({})".format(uuid1, uuid2, name1))
            elif self.uuids[name1] == self.uuids[name2]:
                self.file("HY", "Likely detected a playername change: Lookup {} / Hypixel {} (uuid: {})".format(name1, name2, uuid1))
            else:
                self.file("HY", "Name used in UUID lookup not the same as returned: Lookup {} / Hypixel {} ({})".format(uuid1, uuid2, name1))
        elif uuid1 != uuid2:
            self.file("HY", "Player UUID returned is not the same as used for lookup, somehow: Lookup {} / Hypixel {} ({})".format(uuid1, uuid2, name1))

    def getRequest(self, link):
        """Retrieves request from webpage

        Args:
            link (str): Link to query

        Returns:
            None if failed, content of webpage get if successful
        
        """
        try:
            request = requests.get(link, headers={'User-Agent':str(ua.random), "Connection": "close"}).content
            return json.loads(request)
        except requests.exceptions.ConnectionError as e:
            if self.debug: self.file("REQ", "Failed to request from {} because the server is unresponsive.".format(link))
        except JSONDecodeError as e:
            if self.debug: self.file("REQ", "Failed to request from {} because of JSON Decode Error. Likely due to invalid link or no connection.\nLink: {}\nReturned: {}".format(e, link, request))
        return None

    def file(self, type: str, line: str, isError = True):
        """ Files a line.

        Args:
            type (str): Should be "HY", "MC", or "UNK"
            line (str): The line to file

        Formatted as:
            [ API+ ] Error      | MCAPI/HYAPI: line
        """
        if type == "HY":
            type = "HYAPI"
        elif type == "MC":
            type = "MCAPI"
        elif type == "REQ":
            type = "REQST"
        else:
            type = "OTHER"
        print("[ API+ ] {}     | {}: {}".format("ERROR " if isError else "NOTICE", type, line))