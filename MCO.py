from API import API
from LogMonitor import LogMonitor
from CommandSender import CommandSender as CS
from Config import Config
import time

# Configs and controller
config = Config('./config/config.json', {
    "ownUsers": [
        "cocodef9"
    ],
    "token": "206baa63-dcd2-47f3-b197-b43de4e3301f",
    "logFolder": "C:\\Users\\sjoer\\Appdata\\Roaming\\Minecraft 1.8.9\\logs\\latest.log",
    "autoWho": False,
    "autoInvite": False,
    "autoLeave": True,
    "autoPWarp": True,
    "autoLeavePartyDC": True,
    "enableStatistics-Do-Not-Disable!": True
})
controller = Config('./config/controller.json', {
    "stop": False,
    "getAPI": False
})

# Create a configuration file logger
logger = LogMonitor(config.get("logFolder"), config.get("ownUsers"), True)

# Create an API object
api = API(config.get("token"), True)
# Print API uptime info
print(api.getApiStatus())

# TODO: Add to GUI
autoInviteToggle = True

# Main loop
def startMCO():
    cycle = 0
    while True:

        # Update cycle number (1 per second)
        cycle += 0.1

        if cycle % 60 == 0:
            print(api.getApiStatus())

        # Update logger
        logger.tick()

        # Check for token update
        if logger.newToken != None:
            api.token = logger.newToken
            config.set("token", logger.newToken)
            config.save()
            logger.newToken = None

        # Check for autowho
        if logger.autoWho:
            logger.autoWho = False
            if config.get("autoWho"): CS.who()

        # Check for autoleave
        if logger.autoLeave:
            logger.autoLeave = False
            if config.get("autoLeave"): 
                CS.leave()
                if config.get("autoPWarp"):
                    time.sleep(0.1)
                    CS.pwarp()
            elif config.get("autoPWarp"):
                CS.pwarp()

        # Check for party member DC
        if logger.autoLeavePartyLeave:
            logger.autoLeavePartyLeave = False
            if config.get("autoLeavePartyDC"):
                CS.leave()
                time.sleep(0.1)
                CS.pwarp()
            
        # Check for stats reset (/who)
        if logger.resetStats:
            logger.resetStats = False
            # TODO: Reset stats of players gathered once system in place

        # Check for autoinvite
        if len(logger.autoInvite) > 0 and autoInviteToggle:
            inv = logger.autoInvite.copy()
            logger.autoInvite = []
            if config.get("autoInvite"):
                for player in inv:
                    print("Autoinvite {}?".format(player))
                    #TODO: Add auto statistics check and invite

        # Update player definitions
        if config.get("enableStatistics-Do-Not-Disable!"):
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
            stats = api.getApiStatus()
            print(stats if stats != None else "No stats were found... Is the API down?")

        

        time.sleep(0.1)
    exit()

if __name__ == '__main__':
    startMCO()