from PlayerQueue import PlayerQueue
from API import API
from LogMonitor import LogMonitor
from CommandSender import CommandSender as CS
from Config import Config
import time

print("Initalizing MCO...")

# Configs and controller
print("Loading configuration")
config = Config('./config/config.json', {
    "ownUsers": [
        "cocodef9"
    ],
    "token": "206baa63-dcd2-47f3-b197-b43de4e3301f",
    "logFolder": "C:\\Users\\sjoer\\Appdata\\Roaming\\Minecraft 1.8.9\\logs\\latest.log",
    "playerDetection": {
        "mainLobbyChat": True,
        "mainLobbyJoin": True,
        "gameLobby": True
    },
    "autoCommands": {
        "autoWho": True,
        "autoInvite": True,
        "autoLeave": True,
        "autoPWarp": True,
        "autoPList": True,
        "autoLeavePartyDC": True
    },
    "enableStatistics-Do-Not-Disable!": True
})
print("Loading controller")
controller = Config('./config/controller.json', {
    "stop": False,
    "getAPI": False
})

# Create a configuration file logger
print("Loading log monitor")
logger = LogMonitor(config.get("logFolder"), config.get("ownUsers"), True)

# Create an API object
print("Loading API")
api = API(config.get("token"), True)

# TODO: Add to GUI
autoInviteToggle = True

def loggerTasks(logger: LogMonitor):
    """Runs logger tasks
    
    Args:
        logger (LogMonitor): Logger to check
    """
    # Check for token update
    if logger.newToken != None:
        api.token = logger.newToken
        config.set("token", logger.newToken)
        config.save()
        logger.newToken = None

    # Check for autowho
    if logger.autoWho:
        logger.autoWho = False
        if config.get("autoCommands")["autoWho"]: CS.who()

    # Check for autoplist
    if logger.autoPartyList:
        logger.autoPartyList = False
        if config.get("autoCommands")["autoPList"]: CS.plist()

    # Check for autoleave
    if logger.autoLeave:
        logger.autoLeave = False
        time.sleep(2)
        if config.get("autoCommands")["autoLeave"]: 
            CS.leave()
            if logger.party != None and len(logger.party) > 1 and config.get("autoCommands")["autoPWarp"]:
                time.sleep(0.5)
                CS.pwarp()
        elif config.get("autoCommands")["autoPWarp"]:
            CS.pwarp()

    # Check for party member DC
    if logger.autoLeavePartyLeave:
        logger.autoLeavePartyLeave = False
        if config.get("autoCommands")["autoLeavePartyDC"]:
            CS.leave()
            time.sleep(0.25)
            CS.pwarp()
        
    # Check for stats reset (/who)
    if logger.resetStats:
        logger.resetStats = False
        # TODO: Reset stats of players gathered once system in place

    # Check for autoinvite
    if len(logger.autoInvite) > 0 and autoInviteToggle:
        inv = logger.autoInvite.copy()
        logger.autoInvite = []
        if config.get("autoCommands")["autoInvite"]:
            for player in inv:
                CS.type("/p " + player)
                #TODO: Add auto statistics check and invite

# Main loop
def startMCO():
    
    time.sleep(1)
    CS.plist()
    time.sleep(0.25)
    CS.who()
    
    cycle = 0

    print("Starting main loop")
    while True:

        # Update cycle number (1 per second)
        cycle += 0.1

        if cycle % 60 == 0:
            print(api.getApiStatus())

        # Update logger
        logger.tick()

        # See if there are config changes
        config.hotload()

        # Check for logger tasks
        loggerTasks(logger)

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
    print("Closing MCO")
    exit()

if __name__ == '__main__':
    print("Starting MCO")
    # Print API uptime info
    print("Retrieving API server status...")
    print(api.getApiStatus())
    
    # Tick the logger once to pass any entries existing before starting the overlay
    print("Processing potentially existing log files")
    logger.tick()
    logger.tick()
    
    # Reset logger values
    print("Resetting log file entries")
    logger.resetExposed()

    startMCO()