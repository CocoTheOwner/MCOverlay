from PlayerQueue import PlayerQueue
from Enums import GameOrigin as GO, CommandOrigin as CO, SystemEvents as SE, SystemStatus as SS
from API import API
from LogMonitor import LogMonitor
from CommandSender import CommandSender
from StatInterpreter import getStats
from Config import Config
import time, traceback

defaultConfig = {
    "ownUsername": "cocodef9",
    "token": "206baa63-dcd2-47f3-b197-b43de4e3301f",
    "logFolder": "C:\\Users\\sjoer\\Appdata\\Roaming\\Minecraft 1.8.9\\logs\\latest.log",
    "downloadStatsOfPlayersIn": {
        GO.mainChat: True,
        GO.mainLobby: True,
        GO.gameChat: True,
        GO.gameLobby: True
    },
    "autoCommands": {
        "autoWho": True,
        "autoInvite": True,
        "autoLeave": True,
        "autoLeaveDelaySeconds": 10,
        "autoPWarp": True,
        "autoPList": True,
        "autoTrash": True,
        "autoTrashOof": True,
        "autoLeavePartyDC": True,
        "autoLeavePartyMemberMissing": True
    },
    "autoInviteStatBypass": [
        "dungeoneer1",
        "Prems",
        "gussie842",
        "cocodef9",
        "ReadyPlayerFour",
        "dungeoneer2"
    ],
    "runWhoPListOnStartup": True,
    "enableStatistics-Do-Not-Disable!": True,
    "debug": {
        "API": False,
        "Logs": False,
        "Cycle": False
    },
    "refreshesPerSecond": 10,
    "threads": 10,
    "commandCooldown": 2
}
defaultController = {
    "stop": False,
    "getAPI": False
}

class MCO:

    status = SS.none
    sleepPerCycle = None
    autoLeaveCount = 0
    config = None
    controller = None
    logger = None
    autoInviteToggle = True
    commandSender = None
    api = None
    timeFromStart = time.time()
    startTime = time.time()
    nextCycleInformation = 10
    cycleTimeTenSeconds = 0
    cycle = 0

    def __init__(self):
        
        self.status = SS.startup
        self.file(SE.notify, "Initalizing MCO...")

        # Configuration
        self.file(SE.notify, "Loading configuration")
        self.config = Config('./config/config.json', defaultConfig)

        # Controller
        self.file(SE.notify, "Loading controller")
        self.controller = Config('./config/controller.json', defaultController)

        # Set refresh rate
        self.sleepPerCycle = 1/self.config.get("refreshesPerSecond")

        # LogMonitor
        self.file(SE.notify, "Loading log monitor")
        self.logger = LogMonitor(
            self.config.get("logFolder"), 
            self.config.get("ownUsername"), 
            self.config.get("debug")["Logs"]
        )
        self.status = SS.oldLogs
        self.file(SE.notify, "Loading old logs (if any)")
        self.logger.tick(True)
        self.logger.tick(True)
        self.logger.resetExposed()
        self.status = SS.startup
        self.file(SE.notify, "Loaded old logs")

        # API
        self.file(SE.notify, "Loading API")
        self.api = API(
            self.config.get("token"), 
            int(self.config.get("threads")) - 1,
            self.config.get("debug")["API"]
        )
        self.api.printHypixelStats()
        self.api.printMinecraftStats()

        # CommandSender
        self.file(SE.notify, "Loading Command Sender")
        self.commandSender = CommandSender(self.config.get("commandCooldown"))

        # Update status
        self.status = SS.waiting
        self.file(SE.notify, "Finished initializing")

    def start(self):
        """Runs the overlay
        """

        # Check for initial commands
        if self.config.get("runWhoPListOnStartup"):
            self.file(SE.command, self.commandSender.plist(CO.startup))
            time.sleep(0.25)
            self.file(SE.command, self.commandSender.who(CO.startup))

        # Update status
        self.status = SS.running

        # Main loop
        self.file(SE.notify, "Starting main loop")
        self.timeFromStart = time.time()
        try:
            self.loop()
        except Exception as e:
            self.commandSender.available = False
            self.file(SE.error, "An uncaught exception has been raised in the main loop: {}".format(e))
            self.file(SE.error, "Disabling all command outputs of the program to prevent potential damage")
            self.file(SE.error, traceback.format_exc())
            raise e

        # Shutdown
        self.status = SS.shutdown
        self.file(SE.notify, "Closing MCO")
        exit()

    def loop(self):
        """Runs the main cycle loop
        """
        while True:

            # Update cycle number (1 per second)
            self.cycle += 1

            # Print api & cycle time information
            if self.config.get("debug")["Cycle"]:
                if time.time() - self.startTime >= self.nextCycleInformation:
                    self.nextCycleInformation += 10
                    self.api.printHypixelStats()
                    self.api.printMinecraftStats()
                    self.file(SE.notify, "Overlay load: {load}% | Cycle {cycle} | Last 10s usage: {tens}s | Running for {total}s".format(
                        load = round(self.cycleTimeTenSeconds*10,2), 
                        cycle = self.cycle, 
                        tens = round(self.cycleTimeTenSeconds,2),
                        total = round(time.time() - self.startTime,1)
                    ))
                    self.cycleTimeTenSeconds = 0

            # See if there are config changes
            self.config.hotload()

            # Check for logger tasks
            self.loggerTasks()

            # Update player definitions
            self.statisticsTasks()

            # Check controller
            if self.controllerTask(): break

            # Wait a short while before refreshing
            cycleTime = round(time.time() - self.timeFromStart, 4)
            self.cycleTimeTenSeconds += cycleTime
            time.sleep(max(self.sleepPerCycle - cycleTime, 0))
            self.timeFromStart = time.time()
        
    def loggerTasks(self):
        """Runs logger tasks:
        - Tick the logger
        - Check for new token
        - Check for autowho
        - Check for autoPList
        - Check for party member missing
        - Check for autoLeave
        - Check for autoLeaveParty
        - Check for failedWho's
        - Check for statistics resets
        - Check for autoInvites
        - Check for autoTrash
        """
        
        # Update logger
        self.logger.tick()

        # Check for token update
        if self.logger.newToken != None:
            self.api.token = self.logger.newToken
            self.config.set("token", self.logger.newToken)
            self.config.save()
            self.logger.newToken = None

        # Check for autowho
        if self.logger.autoWho:
            self.logger.autoWho = False
            if self.config.get("autoCommands")["autoWho"]: self.file(SE.command, self.commandSender.who(CO.autowho))

        # Check for autoplist
        if self.logger.autoPartyList:
            self.logger.autoPartyList = False
            if self.config.get("autoCommands")["autoPList"]: self.file(SE.command, self.commandSender.plist(CO.autoplist))

        # Check for logger party member missing tier 2
        if self.logger.partyMemberMissingTwo:
            self.logger.partyMemberMissingTwo = False
            if self.config.get("autoCommands")["autoLeavePartyMemberMissing"]: self.file(CO.partymissing, self.commandSender.pleave(CO.partymissing))

        # Check for autoleave
        if self.logger.autoLeave and self.config.get("autoCommands")["autoLeave"]:
            if round(self.autoLeaveCount * self.sleepPerCycle,2) % 1 == 0:
                self.file(SE.notify, "Attempting autoleave in: {}s".format(self.config.get("autoCommands")["autoLeaveDelaySeconds"] - round(self.autoLeaveCount * self.sleepPerCycle,2)))
            if self.autoLeaveCount * self.sleepPerCycle >= self.config.get("autoCommands")["autoLeaveDelaySeconds"]:
                self.autoLeaveCount = 0
                self.logger.autoLeave = False
                self.file(SE.command, self.commandSender.leave(CO.autoleave))
                if self.logger.party != None and len(self.logger.party) != 0 and self.config.get("autoCommands")["autoPWarp"]:
                    time.sleep(0.75)
                    self.file(SE.command, self.commandSender.pwarp(CO.autoleave))
            else:
                self.autoLeaveCount += 1
        else:
            self.autoLeaveCount = 0

        # Check for party member DC
        if self.logger.autoLeavePartyLeave:
            self.logger.autoLeavePartyLeave = False
            if self.config.get("autoCommands")["autoLeavePartyDC"]:
                self.file(SE.command, self.commandSender.leave(CO.partyleft))
                time.sleep(0.25)
                self.file(SE.command, self.commandSender.pwarp(CO.partyleft))

        # Check for failed autowho's by others
        if len(self.logger.failedWho) > 0:
            for name in self.logger.failedWho:
                # TODO: Add to statistics flags
                self.file(SE.notify, "Failed /who by: " + name)
            self.logger.failedWho = []
            
        # Check for stats reset (/who)
        if self.logger.resetStats:
            self.logger.resetStats = False
            q = PlayerQueue()
            for player in self.logger.party:
                q.add(player, origin=GO.party)
            q.add(self.config.get("ownUsername"))

        # Check for autoinvite
        if len(self.logger.autoInvite) > 0 and self.autoInviteToggle:
            inv = self.logger.autoInvite.copy()
            self.logger.autoInvite = []
            if self.config.get("autoCommands")["autoInvite"]:
                for player in inv:
                    if player in self.config.get("autoInviteStatBypass"):
                        self.file(SE.command, self.commandSender.type("/p " + player, CO.autoinvite))
                    elif True: #TODO: Add auto statistics check and invite
                        self.file(SE.command, self.commandSender.type("/p " + player, CO.autoinvite))

        # Check for autotrash
        if self.logger.toxicReaction != None:
            if self.config.get("autoTrash"):
                if self.config.get("autoTrashOof"):
                    self.file(SE.command, self.commandSender.type(":OOF: " + self.logger.toxicReaction))
                else:
                    self.file(SE.command, self.commandSender.type(self.logger.toxicReaction))
            self.logger.toxicReaction = None

    def controllerTask(self):
        """Runs controller tasks:
        - Process config-stop
        - Process getAPI request
        """
        self.controller.hotload()
        if self.controller.get("stop"):
            self.controller.set("stop", False)
            self.controller.save()
            return True
        if self.controller.get("getAPI"):
            self.controller.set("getAPI", False)
            self.controller.save()
            self.api.printHypixelStats()
            self.api.printMinecraftStats()
            return False

    def statisticsTasks(self):
        """Runs statistics tasks:
        - Retrieving player statistics
        - Processing received statistics
        """

        # Retrieve player download queue
        queue = self.logger.queue.get()

        # Prevent having empty
        if len(queue) == 0:
            return

        # Check if statistics are enabled
        if self.config.get("enableStatistics-Do-Not-Disable!"):
            pd = self.config.get("downloadStatsOfPlayersIn")
            q = {}

            # Check if origin is enabled
            for player in queue.keys():
                origin = queue[player]["origin"]
                if ((origin == GO.mainChat and pd[GO.mainChat]) or
                    (origin == GO.mainLobby and pd[GO.mainLobby]) or
                    (origin == GO.gameChat and pd[GO.gameChat]) or
                    (origin == GO.gameLobby and pd[GO.gameLobby]) or
                    (origin == GO.party)):
                    q[player] = queue[player]

            # Fetch statistics for players
            self.api.fetch(q)
        
        # Retrieve previously retrieved statistics
        stats = self.api.stats.copy()
        self.api.stats.clear()

        # Loop over all statistics
        for stat in stats:
            s = getStats(stats[stat])
            x = {}
            res = ""
            if "DuoRush" in s:
                x = x | s["DuoRush"]
            if "Overall" in s:
                res = "Name: " + s["Overall"]["name"] + ", "
            for key in x.keys():
                res += "{}: {}, ".format(key, x[key])
            self.file(SE.notify, res.removesuffix(", "))
    def file(self, type: str, line: str):
        """Prints a line to console in the proper format
        
        Args:
            type (str): The type of event
            line (str): The line to print
        """
        line = "[SYSTEM] {} | {}: {}".format(
            self.status + (SS.maxStatusLength - len(self.status)) * " ",
            type + (SE.maxEventLength - len(type)) * " ",
            line
        )
        line = line if len(line) < 150 else line[:150].strip() + " (...)"
        print(line)


if __name__ == '__main__':
    MCO().start()