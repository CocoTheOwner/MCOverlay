
import os.path
from types import prepare_class
class logMonitor:
    path = ""
    mtime = 0
    linenumber = 0
    debug = False
    inGame = False
    lobbyCount = 0
    lobbyName = None
    hasQueue = False

    playerQueue = {}

    def __init__(self, path, debug = False):
        self.path = path
        self.debug = debug

    def tick(self):
        # Updates queue
        if (self.mtime != os.path.getmtime(self.path)):
            self.mtime = os.path.getmtime(self.path)
            self.readlog()

    def readlog(self):
        # Stores content of file
        content = ""

        # Retrieve content of file
        with open(self.path, "r") as f:
            content = f.read()

        # Splits the content into lines
        if (self.linenumber == 0):
            content = content.splitlines()
        else:
            content = content.splitlines()[self.linenumber + 1:content.count("\n") + 1]
        if len(content) != 0:

            # Loops over all lines in reversed order
            for line in content:

                # Add one to linecounter
                self.linenumber += 1

                # Process the line
                self.cleanLine(line)

    def cleanLine(self, line: str):
        # (very lightweight) Make sure line is not a stacktrace
        if (not line.startswith("[")):
            return

        # (somewhat heavier) Ensure line is chat
        if (line.count("[Client thread/INFO]: [CHAT]") == 0):
            return

        # (quite heavy) Split line, get useful
        info = line.strip().split("[Client thread/INFO]: [CHAT]")[1].strip()

        # (very light) Empty line check
        if (info == ""):
            return

        # (quite heavy) Usefullness check
        if (not logMonitor.lineIsUseful(info)):
            return

        # (quite light) Lobby check
        if (line.count("You are currently connected to server ") > 0):
            line = line.split("You are currently connected to server ", 1)[1].split(' ')[0]
            if (line != self.lobbyName):
                logMonitor.print("Lobby:[{}] -> [{}]".format(self.lobbyName, line)) if self.lobbyName != None else logMonitor.print("Lobby:[{}]".format(line))
                self.lobbyName = line
            return
            
        if (line.count("Sending you to") > 0):
            line = line.split("Sending you to ", 1)[1].split(' ')[0]
            if (line != self.lobbyName):
                logMonitor.print("Lobby:[{}] -> [{}]".format(self.lobbyName, line)) if self.lobbyName != None else logMonitor.print("Lobby:[{}]".format(line))
                self.lobbyName = line
            return

        # (quite light) Game join check
        if (line.count("Taking you to") > 0):
            logMonitor.print("Game: [" + line.split(" ")[-1].removesuffix("!") + "]")
            return
        
        # (medium heavy) Process the line
        self.process(info)


    # Process a line to retrieve available information
    def process(self, line: str):
        if (line.count("joined the lobby!") > 0):

            # >>> [RANK] username joined the lobby! <<<

            line = line.removeprefix(">>>").split("joined the lobby!")[0].strip().split(" ")
            # [">>>", "[RANK]", "username"] 

            rank = logMonitor.getRank(line[0])

            self.addPlayer(line[-1], rank, -1)

            logMonitor.print("Join: [" + rank + "] " + line[-1] if rank != "NON" else "Join: " + line[-1])
                                                                        
        elif (line.count("has joined") > 0):

            # username has joined (x/y)!

            line = line.split(" ")
            # ["username", "has", "joined", "(x/y)!"]

            # Store player by username
            self.playerQueue[line[0]] = "UNK"

            # Save the amount of players in the lobby
            self.lobbyCount = int(line[-1].replace("(","").replace(")!","").split("/")[0])

            logMonitor.print("JoinR: " + line[0])

        elif (line.count("has quit!") > 0):
            
            # username has quit!

            self.lobbyCount -= 1

            # remove player
            name = line.split(" ")[0]
            self.removePlayer(name)

            logMonitor.print("Quit: " + name)

        elif (line.count("game starts in ") > 0 and line.count(" seconds!") > 0):
            
            logMonitor.print("Time: " + line.split(" ")[-2] + "s")

        elif (line.startswith("[") and line.split(" ")[0].endswith("?]") and (line.split(" ")[1].endswith(":") or line.split(" ")[2].endswith(":")) and line.count(" ") > 1):
            # [STAR?] username: message may contain spaces

            # Prevent single-word lines, which are never a message

            split = line.split(" ")
            # ["[STAR?]", "username:", "message", "may", "contain", "spaces"]
            # ["[STAR?]", "[RANK]", "username:", "message", "may", "contain", "spaces"]

            stars = split[0].removeprefix("[").removesuffix("?]").strip()
            rank = logMonitor.getRank(split[1])
            user = ""
            if (rank == "NON"):
                user = split[1]
                message = line.removeprefix(split[0] + " " + split[1])
            else:
                user = split[2]
                message = line.removeprefix(split[0]).removeprefix(" ").removeprefix(split[1]).removeprefix(" ").removeprefix(split[2])

            message = message.replace("?", "")+"?" if message.endswith("?") else message.replace("?", "").strip()
            while (message.count("  ") > 0):
                message = message.replace("  ", " ")
                

            self.addPlayer(user.replace(":",""), rank, stars)

            logMonitor.print("Chat: [{}] {}{} {}".format(stars, "[" + rank + "] " if rank != "NON" else "", user, message.strip()))
        else:
            logMonitor.print("\n\n\n\nUNPROCESSED LINE!\n" + line + "\n\n\n\n")

    
    def getRank(line: str):
        if (line.__contains__("[VIP]")):
            return "VIP"
        if (line.__contains__("[VIP+]")):
            return "VIP+"
        if (line.__contains__("[MVP]")):
            return "MVP"
        if (line.__contains__("[MVP+]")):
            return "MVP+"
        if (line.__contains__("[MVP++]")):
            return "MVP++"
        if (line.__contains__("[Helper]")):
            return "Helper"
        if (line.__contains__("[YOUTUBE]")):
            return "Admin"
        if (line.__contains__("[Admin]")):
            return "Admin"
        if (line.__contains__("[Owner]")):
            return "Owner"
        return "NON"
            
    """
    Definitions of useless chat lines.
    Tread carefully. 
    Include as much information as possible to prevent accidental removing.
    """
    def lineIsUseful(line: str):
        line = line.strip()
        if (line.count("You are AFK") > 0): return False
        if (line.count("Friend > ") > 0): return False
        if (line.count("Guild > ") > 0): return False
        if (line.count("You tipped") > 0 and line.count("players!") > 0): return False
        if (line.count("found a") > 0 and line.count("Mystery Box!") > 0): return False
        if (line.count("Watchdog has banned") > 0 and line.count("players in the last") > 0): return False
        if (line.count("Staff have banned an additional") > 0 and line.count("in the last") > 0): return False
        if (line.count("Unknown command. Type \"help\" for help.") > 0): return False
        if (line.count("[Mystery Box]") > 0 and line.count("found") > 0): return False
        if (line == "[WATCHDOG ANNOUNCEMENT]"): return False
        if (line == "Blacklisted modifications are a bannable offense!"): return False
        if (line == "A player has been removed from your lobby."): return False
        if (line == "Use /report to continue helping out the server!"): return False
        if (line == "You were kicked while joining that server!"): return False
        if (line == "This server is full! (Server closed)"): return False
        return True

    def addPlayer(self, name, rank, stars):
        self.playerQueue[name] = {rank, stars}
        self.hasQueue = len(self.playerQueue) > 0
        
    def removePlayer(self, name):
        for i,element in enumerate(self.playerQueue):
            if (element[0] == name):
                del self.playerQueue[i]
            self.hasQueue = len(self.playerQueue) > 0

    def getPlayers(self):
        q = self.playerQueue.copy()
        self.playerQueue = {}
        self.hasQueue = False
        return q

    def print(string):
        
        # (quite heavy) Add line to log
        with open("./config/log.txt", "a") as f:
            f.write(string + "\n")

        print(string)
