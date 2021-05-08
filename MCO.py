from api import API
from logMonitor import logMonitor
from config import Config
import time

# Configs and controller
config = Config('./config/config.json', {
    "ownUsers": [
        "cocodef9"
    ],
    "token": "206baa63-dcd2-47f3-b197-b43de4e3301f",
    "logFolder": "C:\\Users\\sjoer\\Appdata\\Roaming\\Minecraft 1.8.9\\logs\\latest.log"
})
players = Config('./logs/players.json', {})
controller = Config('./config/controller.json', {
    "stop": False,
    "lineCap": -1
})

# Create a configuration file logger
logger = logMonitor(config.get("logFolder"), False)

# Create an API object
api = API(players.config, config.get("token"))

# Create or reset controller file
open("./controller.txt", "w").close()

# Main loop
def startMCO():
    cycle = 0
    while True:

        # Update cycle number
        cycle += 1

        if (cycle % 100 == 0): print("Cycled 10 seconds")

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
        api.fetch(logger.queue.get(), players)

        # Check controller
        controller.load()
        lc = controller.get("lineCap")
        if controller.get("stop") or (lc != -1 and logger.actualLineNumber >= lc):
            break

        time.sleep(0.1)
    exit()

if __name__ == '__main__':
    startMCO()