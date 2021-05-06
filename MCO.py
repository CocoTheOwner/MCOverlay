from api import API
from logMonitor import logMonitor
from config import Config
import time
from multiprocessing import Process, Lock

# Default configuration
defaultConfig = {
    "ownUsers": [
        "cocodef9"
    ],
    "token": "token",
    "logFolder": "C:\\Users\\sjoer\\Appdata\\Roaming\\Minecraft 1.8.9\\logs\\latest.log"
}

# Load configuration file (if empty, loads defaultConfig)
config = Config('./config/config.json', defaultConfig)
players = Config('./config/players.json', {})

# Save the configuration file
config.save()

# Create a configuration file logger
logger = logMonitor(config.get("logFolder"), True)

# Create an API object
api = API(players.config, config.get("token"))

# Reset log
open('./config/log.txt', 'w').close()


def start():
    while(True):
        logger.tick()
        if (logger.hasQueue):
            for player in logger.getPlayers():
                uuid = api.minecraft(player)
                players.set(player, uuid)
                stats = api.hypixel(uuid)
                players.set(uuid, stats)

        time.sleep(0.1)



def f(l, i):
    l.acquire()
    try:
        print('hello world', i)
    finally:
        l.release()

if __name__ == '__main__':
    #lock = Lock()
    start()
    #for num in range(10):
    #    Process(target=f, args=(lock, num)).start()