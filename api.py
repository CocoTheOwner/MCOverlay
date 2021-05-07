# -*- coding: utf-8 -*-
from config import Config
import json
from json.decoder import JSONDecodeError
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
"""Module for retrieving data from several preset API pages"""
class API:
    players = {}
    token = ""
    debug = False

    # TODO: Queue party and self for statistics refresh when requested

    def __init__(self, players: dict, token: str, debug = False):
        self.players = players
        self.token = token
        self.debug = debug

    def fetch(self, playerQueue, file: Config):
        """Fetches all player data from a queue

        Args:
            playerQueue (dict): Queue of players to get stats of
            file (Config): Configuration file to write results to and take existing results from

        """
        threads = []
        with ThreadPoolExecutor(max_workers=50) as executor:
            count = 0
            total = len(playerQueue)
            for player in playerQueue:
                count += 1
                threads.append(executor.submit(self.getPlayerData, player, file))

            for task in as_completed(threads):
                if (self.debug): print("Completed task ({}/{}) | Result: {}".format(total - count, total, str(task.result())))
                count -= 1

    def getPlayerData(self, player, file: Config):
        """Retrieves player data of a player
        
        Args:
            player (str): Playername
            file (Config): Configuration file to write results to and take existing results from

        """
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
            if (self.debug): print("Completed data retrieval for " + player)

    def hypixel_stats(self):
        """Retrieve hypixel API server information

        Returns:
            None if failed, record with information if successful
        """
        request = API.getRequest("https://api.hypixel.net/key?key={}".format(self.token))
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
        #if (self.debug): print("Downloading stats of {} ({})".format(player, uuid))
        print("Downloading stats of {} ({})".format(player, uuid))
        request = API.getRequest("https://api.hypixel.net/player?key={}&uuid={}".format(self.token, uuid))
        if request == None or request["success"] != "true":
            self.players[uuid] = player
            return None
        else:
            self.players[uuid] = request["player"]
            return request["player"]

    def minecraft(self, username):
        """Retrieves UUID of a player

        Args:
            username (str): Username of the player to get data from

        Returns:
            UUID string

        """

        # Prevent loading same username twice
        if (username in self.players):
            if type(self.players[username]) == str:
                return self.players[username]
            elif type(self.players[username]) == dict:
                return self.players[username]["uuid"]
        
        # Get UUID from server
        if (self.debug): print("Downloading UUID of {}".format(username))
        request = API.getRequest("https://api.mojang.com/users/profiles/minecraft/" + username)
        if request != None:
            self.players[username] = request["id"]
            return request["id"] 
        else:
            return 0

    def getRequest(link):
        """Retrieves request from webpage

        Args:
            link (str): Link to query

        Returns:
            None if failed, content of webpage get if successful
        
        """
        content = None

        try:
            content = json.loads(requests.get(link, headers={'Connection': 'close'}).content)
        except JSONDecodeError as e:
            print("Failed to request from {} because of JSON Decode Error. Likely due to invalid link or no connection.".format(e))
        except Exception as e:
            print("Failed to request from {} because of an Exception:\n{}".format(link, e))

        return content