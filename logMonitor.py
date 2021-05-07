
from config import Config
import os.path
from types import prepare_class
class logMonitor:

    failedLine = Config("./config/missedline.json", {})

    logFilePath = ""
    modificationTime = 0
    lineNumber = 0
    debug = False
    inGame = False
    lobbyCount = 0
    lobbyName = None
    hasQueue = False
    newToken = None
    playerQueue = {}

    def __init__(self, logFilePath, debug = False):
        open('./config/log.txt', 'w').close()
        self.logFilePath = logFilePath
        self.debug = debug

    def tick(self):
        """Ticks the logger. Only ticks if there is a log change.
        """
        if (self.modificationTime != os.path.getmtime(self.logFilePath)):
            self.modificationTime = os.path.getmtime(self.logFilePath)
            self.readlog()

    def readlog(self):
        """Reads the log file
        """
        # Retrieve log file content
        content = open(self.logFilePath, "r").read().splitlines()

        # Selects log lines that need to be seen
        if (self.lineNumber != 0): content = content[self.lineNumber + 1:content.count("\n") + 1]

        # Loops over all lines in reversed order
        for line in content:

            # Add one to linecounter
            self.lineNumber += 1

            # Clean and process the line
            line = self.cleanLine(line)
            if line != None: self.process(line) 

    def cleanLine(self, line: str):
        """Cleans an inputted line and prevents unimportant lines from being parsed

        Args:
            line (str): The line to clean / process

        Returns:
            line (str): Cleaned line or None (if the line was rejected)

        """
        if (not line.startswith("[")): return None                           # (light)  Make sure line is not a stacktrace
        if (line.count("[Client thread/INFO]: [CHAT]") == 0): return None    # (medium) Ensure line is chat
        line = line.strip().split("[Client thread/INFO]: [CHAT]")[1].strip() # (medium) Split line, get useful
        if (line == ""): return None                                         # (light)  Empty line check
        if (not logMonitor.lineIsUseful(line)): return None                  # (medium) Usefullness check
        return line

    def process(self, line: str):
        """Process a line

        Args:
            line (str): The line to process
        
        """
        if (line.startswith("[") and line.split(" ")[0].endswith("?]") and (line.split(" ")[1].endswith(":") or line.split(" ")[2].endswith(":")) and line.count(" ") > 1):
            self.chatMessage(line)
        elif (line.startswith("You are currently connected to server ") or line.startswith("Sending you to")):
            self.moveLobby(line)
        elif (line.startswith("Taking you to")):
            logMonitor.print("Game: [" + line.split(" ")[-1].removesuffix("!") + "]")
            return
        elif (line.count("joined the lobby!") > 0):
            self.joinLobby(line)
        elif (line.count("has joined") > 0):
            self.playerJoinGame(line)
        elif (line.endswith("has quit!")):
            self.quitGame(line)
        elif (line.startswith("The game starts in") and line.endswith("seconds!")):
            self.gameTime(line)
        elif (line.startswith("Your new API key is ")):
            self.newApiKey(line)
        else:
            self.unprocessed(line)


    """ Chat message events """
    def chatMessage(self, line: str):
        """Process a lobby chat event

        Args:
            line (str): Line to process

        Examples:
            [STAR?] username: message may contain spaces
            [STAR?] [RANK] username: message may contain spaces
        """

        split = line.split(" ")
        # ["[STAR?]", "username:", "message", "may", "contain", "spaces"]
        # ["[STAR?]", "[RANK]", "username:", "message", "may", "contain", "spaces"]

        # Retrieve stars
        stars = split[0].removeprefix("[").removesuffix("?]")

        # Retrieve rank, username and message
        if split[1].endswith(":"):
            rank = "NON"
            user = split[1].removesuffix(":")
            message = " ".join(split[1:])
        else:
            rank = logMonitor.getRank(split[1])
            user = split[2].removesuffix(":")
            message = " ".join(split[2:])

        # Clean the message
        message = message.replace("?", "")+"?" if message.endswith("?") else message.replace("?", "").strip()
        while (message.count("  ") > 0):
            message = message.replace("  ", " ")
            
        # Add the player to the playerqueue
        self.addPlayer(user, rank, stars)

        logMonitor.print("Chat: [{}] {}{} {}".format(stars, "[" + rank + "] " if rank != "NON" else "", user, message.strip()))
    
    def moveLobby(self, line: str):
        """Process a lobby move event

        Args:
            line (str): Line to process

        Example:
            You are currently connected to server x
            Sending you to x
        
        """

        # Reset the lobby counter
        self.lobbyCount = 0

        # Retrieve the lobby name
        name = line.removeprefix("You are currently connected to server").removeprefix("Sending you to").strip().split(' ')[0]

        # Set the lobby name if changed
        if (name != self.lobbyName):
            logMonitor.print("Lobby:[{}] -> [{}]".format(self.lobbyName, name)) if self.lobbyName != None else logMonitor.print("Lobby:[{}]".format(name))
            self.lobbyName = name

    def joinLobby(self, line: str):
        """Process a lobby join event

        Args:
            line (str): Line to process

        Example:
            >>> [RANK] username joined the lobby! <<<
        """

        # Reset the lobby counter
        self.lobbyCount = 0

        line = line.removeprefix(">>>").removesuffix("joined the lobby!").strip().split(" ")
        # ["[RANK]", "username"]

        rank = logMonitor.getRank(line[0])
        name = line[1]

        self.addPlayer(name, rank, -1)

        logMonitor.print("Join: [" + rank + "] " + name if rank != "NON" else "Join: " + name)

    def playerJoinGame(self, line: str):
        """Process a player game lobby join event

        Args:
            line (str): Line to process

        Example:
            username has joined (x/y)!
        """
        line = line.split(" ")
        # ["username", "has", "joined", "(x/y)!"]

        name = line[0]
        joinNumber = int(line[-1].replace("(","").replace(")!","").split("/")[0])

        # Store player by username
        self.playerQueue[name] = "UNK"

        # Save the amount of players in the lobby
        self.lobbyCount = joinNumber

        logMonitor.print("Join: {} ({})".format(name, joinNumber))
  
    def quitGame(self, line: str):
        """Process a game lobby quit event

        Args:
            line (str): Line to process

        Example:
            username has quit!
        """

        # Remove one player from the lobby count
        self.lobbyCount -= 1

        # Remove the player from the queue
        name = line.removesuffix(" has quit!").strip()
        self.removePlayer(name)

        logMonitor.print("Quit: {} {}".format(name, self.lobbyCount))

    def gameTime(self, line: str):
        """Process a game lobby time event

        Args:
            line (str): Line to process

        Example:
            The game starts in x seconds!
        """

        time = line.removeprefix("The game starts in").removesuffix("seconds!").strip()

        logMonitor.print("Time: " + time + "s")

    def newApiKey(self, line: str):
        """Process a new api key event

        Args:
            line (str): Line to process

        Examples:
            Your new API key is x
        """

        # Retrieve key
        key = line.removeprefix("Your new API key is ").strip()

        # Store key
        self.newToken = key

        logMonitor.print("API: " + self.newToken)

    def unprocessed(self, line: str):
        """Process an unprocessed message event

        Args:
            line (str): Line to process
        """
        logMonitor.print("\n\n\n\nUNPROCESSED LINE!\n" + line + "\n\n\n\n")

    """ Utility """
    def getRank(line: str):
        """Retrieves a rank from a line. Returns non if none is found

        Args:
            line (str): Line to search

            
        Returns: 
            str: One of: 
            VIP, VIP+, MVP, MVP+, MVP++, Helper, Admin, YOUTUBE, Owner or NON

        """
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
            return "YOUTUBE"
        if (line.__contains__("[Admin]")):
            return "Admin"
        if (line.__contains__("[Owner]")):
            return "Owner"
        return "NON"

    def lineIsUseful(line: str):
        """Checks for line usefulness

        Args:
            line (str): The line to check

        Returns:
            bool: True if useful, false if not.

        """
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
        if (line == "You already have an API Key, are you sure you want to regenerate it?"): return False
        if (line == "Blacklisted modifications are a bannable offense!"): return False
        if (line == "A player has been removed from your lobby."): return False
        if (line == "Use /report to continue helping out the server!"): return False
        if (line == "You were kicked while joining that server!"): return False
        if (line == "This server is full! (Server closed)"): return False
        return True

    def addPlayer(self, name: str, rank: str, stars: int):
        """Adds a player to the playerqueue by name, rank and stars

        Args:
            name (str): The name of the player
            rank (str): The rank of the player
            stars (int): The amount of stars for the player
        """
        self.playerQueue[name] = {rank, stars}
        self.hasQueue = len(self.playerQueue) > 0
        
    def removePlayer(self, name: str):
        """Removes the player by given argument from the playerqueue

        Args:
            name (str): Name of the player to remove
        """
        for i,element in enumerate(self.playerQueue):
            if (element[0] == name):
                del self.playerQueue[i]
            self.hasQueue = len(self.playerQueue) > 0

    def getPlayers(self):
        """Retrieves all players currently in the queue and clears the queue

        Returns:
            dict: Contains all queued players
        """
        q = {}
        if (self.hasQueue):
            q = self.playerQueue.copy()
            self.playerQueue = {}
            self.hasQueue = False
        return q

    def print(string):
        """Saves a line to a log file and prints the line to console
        """
        with open("./config/log.txt", "a") as f:
            f.write(string + "\n")
        print(string)