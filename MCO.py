from api import API
from logMonitor import logMonitor
from config import Config
import time

# Default configuration
defaultConfig = {
    "ownUsers": [
        "cocodef9"
    ],
    "token": "token",
    "logFolder": "C:\\Users\\sjoer\\Appdata\\Roaming\\Minecraft 1.8.9\\logs\\latest.log"
}

# Load configuration file (if empty, loads defaultConfig)
config = Config('./config.json', defaultConfig)

# Save the configuration file
config.save()

# Create a configuration file logger
logger = logMonitor(config.get("logFolder"))

# Create an API object
api = API()

def start():
    for user in config.get("ownUsers"):
        print("User: {} has UUID: {}".format(user, api.minecraft(user)))
    while(True):
        logger.tick()
        time.sleep(0.1)


if (__name__ == "__main__"):
    start()