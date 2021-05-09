from API import API
from LogMonitor import LogMonitor
from Config import Config
import time

# Configs and controller
config = Config('./config/config.json', {
    "ownUsers": [
        "cocodef9"
    ],
    "token": "206baa63-dcd2-47f3-b197-b43de4e3301f",
    "logFolder": "C:\\Users\\sjoer\\Appdata\\Roaming\\Minecraft 1.8.9\\logs\\latest.log"
})
controller = Config('./config/controller.json', {
    "stop": False,
    "getAPI": False
})

# Create a configuration file logger
logger = LogMonitor(config.get("logFolder"), True)

# Create an API object
api = API(config.get("token"), False)
# Print API uptime info
stats = api.hypixel_stats()
print(stats if stats != None else "No stats were found... Is the API down?")

# Main loop
def startMCO():
    cycle = 0
    while True:

        # Update cycle number
        cycle += 1

        if cycle % 100 == 0: print("Cycled 10 seconds")

        # Update logger
        logger.tick()

        # Check for token update
        if logger.newToken != None:
            api.token = logger.newToken
            config.set("token", logger.newToken)
            config.save()
            logger.newToken = None

        # Update player definitions
        api.fetch(logger.queue.get())

        # Check controller
        controller.load()
        if controller.get("stop"):
            controller.set("stop", False)
            controller.save()
            break
        if controller.get("getAPI"):
            controller.set("getAPI", False)
            controller.save()
            stats = api.hypixel_stats()
            print(stats if stats != None else "No stats were found... Is the API down?")

        

        time.sleep(0.1)
    exit()

if __name__ == '__main__':
    startMCO()