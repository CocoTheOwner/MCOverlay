
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
                print("Lobby: New: {}, Previous: {}".format(line, self.lobbyName))
                self.lobbyName = line
            return

        # (quite light) Game join check
        if (line.count("Taking you to") > 0):
            print("Game: " + line.split(" ")[-1].removesuffix("!"))
            return
        
        # (medium heavy) Process the line
        self.process(info)


    # Process a line to retrieve available information
    def process(self, line: str):
        if (line.count("joined the lobby!") > 0):

            # >>> [RANK] username joined the lobby! <<<

            line = line.split("joined the lobby!")[0].strip().split(" ")
            # [">>>", "[RANK]", "username"] 

            rank = logMonitor.getRank(line[-2])

            self.addPlayer(line[-1], rank)

            print("Join: [" + rank + "] " + line[-1] if rank != "NON" else "Join: " + line[-1])
                                                                        
        elif (line.count("has joined") > 0):

            # username has joined (x/y)!

            line = line.split(" ")
            # ["username", "has", "joined", "(x/y)!"]

            # Store player by username
            self.playerQueue[line[0]] = "UNK"

            # Save the amount of players in the lobby
            self.lobbyCount = int(line[-1].replace("(","").replace(")!","").split("/")[0])

            print("Join: " + line[0])

        elif (line.count("has quit!") > 0):
            
            # username has quit!

            self.lobbyCount -= 1

            # remove player
            name = line.split(" ")[0]
            self.removePlayer(name)

            print("Quit: " + name)

        elif (line.count("game starts in ") > 0 and line.count(" seconds!") > 0):
            
            print("Time: " + line.split(" ")[-2] + "s")

        elif (line.count(" ") > 0):
            # [STAR?] username: message may contain spaces

            # Prevent single-word lines, which are never a message

            split = line.split(" ")
            # ["[STAR?]", "username:", "message", "may", "contain", "spaces"]

            message = line.removeprefix(split[0] + " " + split[1] + " ")
            message = message.replace("?", "")+"?" if message.endswith("?") else message.replace("?", "")
            while (message.count("  ") > 0):
                messge = message.replace("  ", " ")
                

            self.addPlayer(split[1].removesuffix(":").strip(), split[0].removeprefix("[").removesuffix("?]"))

            print("Chat: {} {}".format(split[1], message))
        else:
            print("Line: " + line)

    
    def getRank(line: str):
        if (line.__contains__(" [VIP] ")):
            return "VIP"
        if (line.__contains__(" [VIP+] ")):
            return "VIP+"
        if (line.__contains__(" [MVP] ")):
            return "MVP"
        if (line.__contains__(" [MVP+] ")):
            return "MVP+"
        if (line.__contains__(" [MVP++] ")):
            return "MVP++"
        return "NON"
            
    """
    Definitions of useless chat lines.
    Tread carefully. 
    Include as much information as possible to prevent accidental removing.
    """
    def lineIsUseful(line: str):
        if (line.count("You are AFK") > 0):
            return False
        if (line.count("Friend > ") > 0):
            return False
        if (line.count("You tipped") > 0 and line.count("players!") > 0):
            return False
        if (line.count("found a") > 0 and line.count("Mystery Box!") > 0):
            return False
        if (line.count("Watchdog has banned") > 0 and line.count("players in the last") > 0):
            return False
        if (line.count("Staff have banned an additional") > 0 and line.count("in the last") > 0):
            return False
        if (line.strip() == "[WATCHDOG ANNOUNCEMENT]"):
            return False
        if (line.strip() == "Blacklisted modifications are a bannable offense!"):
            return False
        return True

    def addPlayer(self, name, value):
        self.playerQueue[name] = value
        self.hasQueue = len(self.playerQueue) > 0
        
    def removePlayer(self, name):
        if (name in self.playerQueue):
            del self.playerQueue[name]
            self.hasQueue = len(self.playerQueue) > 0
