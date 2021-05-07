from api import API
from logMonitor import logMonitor
from config import Config
import time

# Load configuration file (if empty, loads defaultConfig)
config = Config('./config/config.json', {
    "ownUsers": [
        "cocodef9"
    ],
    "token": "206baa63-dcd2-47f3-b197-b43de4e3301f",
    "logFolder": "C:\\Users\\sjoer\\Appdata\\Roaming\\Minecraft 1.8.9\\logs\\latest.log"
})
players = Config('./config/players.json', {})

# Create a configuration file logger
logger = logMonitor(config.get("logFolder"), True)

# Create an API object
api = API(players.config, config.get("token"))

# Main loop
def startMCO():
    while(True):

        # Update logger
        logger.tick()

        # Check for token update
        if logger.newToken != None:
            print("New token: " + logger.newToken)
            api.token = logger.newToken
            config.set("token", logger.newToken)
            config.save()
            logger.newToken = None

        # Update player definitions
        api.fetch(logger.getPlayers(), players)
                
        time.sleep(0.1)

if __name__ == '__main__':
    startMCO()