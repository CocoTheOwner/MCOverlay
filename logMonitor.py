import os
from ChatEvents import ChatEvents as CE, GameStatus as GS
from PlayerQueue import PlayerQueue
class LogMonitor:

    combinedLog = "./logs/combined.txt"    
    if not os.path.exists("/".join(combinedLog.split("/")[:-1])):
        os.makedirs("/".join(combinedLog.split("/")[:-1]))
    open(combinedLog, "w").close() # Reset file

    lobbyName = None
    mainUsers = None
    newToken = None
    debug = None

    modificationTime = 0
    lineNumber = 0
    playersInLobby = 0


    status = GS.unknown

    queue = PlayerQueue()

    def __init__(self, logFilePath: str, mainUsers, debug = False):
        self.logFilePath = logFilePath
        self.mainUsers = mainUsers
        self.debug = debug

    def tick(self):
        """Ticks the logger. Only ticks if there is a log change.
        """
        if self.modificationTime != os.path.getmtime(self.logFilePath):
            self.modificationTime = os.path.getmtime(self.logFilePath)
            self.readlog()

    def readlog(self):
        """Reads the log file
        """
        # Retrieve log file content
        content = open(self.logFilePath, "r").read().splitlines()

        # If the length of the log file is shorter than the linenumber, reset the linenumber
        if len(content) < self.lineNumber:
            self.lineNumber = 0
            if self.debug: print("Reset linenumber. Likely due to Minecraft restarting.")
        # Selects log lines that need to be seen
        if self.lineNumber != 0: content = content[self.lineNumber + 1:len(content)]

        # Loops over all lines in reversed order
        for line in content:

            # Add one to linecounter
            self.lineNumber += 1

            # Clean and process the line
            line = self.cleanLine(line)
            if line == None:
                continue
            elif not LogMonitor.lineIsUseful(line):
                self.file("USLS", line, False)
            else:
                self.process(line) 

    def cleanLine(self, line: str):
        """Cleans an inputted line and prevents unimportant lines from being parsed

        Args:
            line (str): The line to clean / process

        Returns:
            line (str): Cleaned line or None (if the line was rejected)

        """
        if line.count("[Client thread/INFO]: [CHAT]") != 0: 
            split = line.strip().split("[Client thread/INFO]: [CHAT]")[1].strip()
            if split != "":
                return split
            self.file(CE.removed, line)
        return None

    def process(self, line: str):
        """Process a line

        Args:
            line (str): The line to process
        
        """
        if line.startswith("[") and line.split(" ")[0].endswith("?]") and (line.split(" ")[1].endswith(":") or line.split(" ")[2].endswith(":")) and line.count(" ") > 1:
            self.lobbyChatMessage(line)
        elif line.startswith("You are currently connected to server ") or line.startswith("Sending you to") or line.startswith("Taking you to"):
            self.moveLobby(line)
        elif line == "Bed Wars":
            self.endGame()
        elif line.count("joined the lobby!") > 0:
            self.joinLobby(line)
        elif line.count("has joined") > 0:
            self.playerJoinGame(line)
        elif line.startswith("ONLINE:"):
            self.whoCommand(line)
        elif line.endswith("has quit!"):
            self.quitGame(line)
        elif line.startswith("The game starts in") and line.count("second") > 0:
            self.gameTime(line)
        elif line == "We don't have enough players! Start cancelled.":
            self.file("Game", "Start cancelled")
        elif line.startswith("Your new API key is "):
            self.newAPIKey(line)
        else:
            self.unprocessed(line)

    """ Chat message events """
    def lobbyChatMessage(self, line: str):
        """Process a lobby chat event

        Args:
            line (str): Line to process

        Examples:
            [STAR?] username: message may contain spaces
            [STAR?] [RANK] username: message may contain spaces

        Status:
            mainLobby
        """
        self.status = GS.mainLobby

        split = line.split(" ")
        # ["[STAR?]", "username:", "message", "may", "contain", "spaces"]
        # ["[STAR?]", "[RANK]", "username:", "message", "may", "contain", "spaces"]

        # Retrieve stars
        stars = split[0].removeprefix("[").removesuffix("?]")

        # Retrieve rank, username and message
        if split[1].endswith(":"):
            rank = "NON"
            user = split[1].removesuffix(":")
            message = " ".join(split[2:])
        else:
            rank = LogMonitor.getRank(split[1])
            user = split[2].removesuffix(":")
            message = " ".join(split[3:])

        # Clean the message
        message = message.replace("?", "")+"?" if message.endswith("?") else message.replace("?", "").strip()
        while (message.count("  ") > 0):
            message = message.replace("  ", " ")

        # Check if the player is the main player
        if user in self.mainUsers:
            return
            
        # Add the player to the playerqueue
        self.queue.add(user, rank, stars)

        rank = "[" + rank + "] " if rank != "NON" else ""

        self.file(CE.chat, "[{}] {}{}: {}".format(stars, rank, user, message.strip()))
    
    def moveLobby(self, line: str):
        """Process a lobby move event

        Args:
            line (str): Line to process

        Example:
            You are currently connected to server x
            Sending you to x
            Taking you to x
        
        Status:
            Unchanged
        """

        # Reset the lobby counter
        self.playersInLobby = 0

        # Retrieve the lobby name
        name = line.removeprefix("You are currently connected to server").removeprefix("Sending you to").removeprefix("Taking you to").strip().split(' ')[0]

        # Set the lobby name if changed
        if name != self.lobbyName:
            self.file(CE.lobby, "[{}] -> [{}]".format(self.lobbyName, name))
            self.playersInLobby = 0
            self.lobbyName = name

    def joinLobby(self, line: str):
        """Process a lobby join event

        Args:
            line (str): Line to process

        Example:
            >>> [RANK] username joined the lobby! <<<

        Status:
            MainLobby
        """
        self.status = GS.mainLobby

        # Reset the lobby counter
        self.playersInLobby = 0

        line = line.removeprefix(">>>").removesuffix("joined the lobby!").strip().split(" ")
        # ["[RANK]", "username"]

        rank = LogMonitor.getRank(line[0])
        rank = "[" + rank + "] " if rank != "NON" else ""
        name = line[1]

        self.queue.add(name, rank, -1)


        self.file(CE.player, "{}{}".format(rank, name))

    def endGame(self):
        """Process a game end event

        Example:
            "Bed Wars"

        Status:
            Based on current status type, switches to:
            MainLobby (if in game)
            InGame (if in lobby)
        """
        if self.status == GS.inGame:
            self.status = GS.mainLobby
            self.file(CE.game, "Finished")
        else:
            self.status = GS.inGame
            self.file(CE.game, "Started")

    def playerJoinGame(self, line: str):
        """Process a player game lobby join event

        Args:
            line (str): Line to process

        Example:
            username has joined (x/y)!

        Status:
            GameLobby
        """
        self.status = GS.gameLobby

        line = line.split(" ")
        # ["username", "has", "joined", "(x/y)!"]

        name = line[0]
        joinNumber = int(line[-1].replace("(","").replace(")!","").split("/")[0])

        # Store player by username
        self.queue.add(name, "UNK", -1)

        # Save the amount of players in the lobby
        self.playersInLobby = joinNumber

        self.file(CE.join, "{} ({})".format(name, joinNumber))
    
    def whoCommand(self, line: str):
        """Process a who command

        Args:
            line (str): Line to process

        Example:
            ONLINE: username, username, username, username, ...

        Status:
            GameLobby
        """
        self.status = GS.gameLobby
        line = line.removeprefix("ONLINE: ").split(", ")
        self.playersInLobby = len(line)
        for username in line:
            self.file(CE.who, username)
            self.queue.add(username, "UNK", -1)
        self.file(CE.who, "{} players in the lobby".format(len(line)))

    def quitGame(self, line: str):
        """Process a game lobby quit event

        Args:
            line (str): Line to process

        Example:
            username has quit!

        Status:
            GameLobby
        """
        self.status = GS.gameLobby

        # Remove one player from the lobby count
        self.playersInLobby -= 1

        # Remove the player from the queue
        name = line.removesuffix(" has quit!").strip()
        self.queue.delete(name)

        self.file(CE.quit, "{} ({})".format(name, self.playersInLobby))

    def gameTime(self, line: str):
        """Process a game lobby time event

        Args:
            line (str): Line to process

        Example:
            The game starts in x seconds!

        Status:
            GameLobby
        """
        self.status = GS.gameLobby

        time = line.removeprefix("The game starts in").removesuffix("seconds!").strip()

        self.file(CE.time, time + "s")

    def newAPIKey(self, line: str):
        """Process a new api key event

        Args:
            line (str): Line to process

        Examples:
            Your new API key is x

        Status:
            MainLobby
        """

        self.status = GS.mainLobby

        # Retrieve key
        key = line.removeprefix("Your new API key is ").strip()

        # Store key
        self.newToken = key

        self.file(CE.api, key)

    def unprocessed(self, line: str):
        """Process an unprocessed message event

        Args:
            line (str): Line to process

        Status:
            unchanged
        """
        self.file(CE.uncharted, line)

    """ Utility """
    def getRank(line: str):
        """Retrieves a rank from a line. Returns non if none is found

        Args:
            line (str): Line to search

            
        Returns: 
            str: One of: 
            VIP, VIP+, MVP, MVP+, MVP++, Helper, Admin, YOUTUBE, Owner or NON

        """
        if line.__contains__("[VIP]"):
            return "VIP"
        if line.__contains__("[VIP+]"):
            return "VIP+"
        if line.__contains__("[MVP]"):
            return "MVP"
        if line.__contains__("[MVP+]"):
            return "MVP+"
        if line.__contains__("[MVP++]"):
            return "MVP++"
        if line.__contains__("[Helper]"):
            return "Helper"
        if line.__contains__("[YOUTUBE]"):
            return "YOUTUBE"
        if line.__contains__("[Admin]"):
            return "Admin"
        if line.__contains__("[Owner]"):
            return "Owner"
        return "NON"

    def lineIsUseful(line: str):
        """Checks for line usefulness

        Args:
            line (str): The line to check

        Returns:
            bool: True if useful, false if not.

        """
        if line == "": return False
        if line == "[WATCHDOG ANNOUNCEMENT]": return False
        if line == "This server is full! (Server closed)": return False
        if line == "A player has been removed from your lobby.": return False
        if line == "You were kicked while joining that server!": return False
        if line == "Use /report to continue helping out the server!": return False
        if line == "Blacklisted modifications are a bannable offense!": return False
        if line == "You already have an API Key, are you sure you want to regenerate it?": return False

        if line.replace("?","") == "": return False
        if line.replace("-","") == "": return False
        if line.count("Guild > ") > 0: return False
        if line.count("Friend > ") > 0: return False
        if line.count("You are AFK") > 0: return False
        if line.count("You purchased") > 0: return False
        if line.count("Unknown command. Type \"help\" for help.") > 0: return False
        if line.count("[Mystery Box]") > 0 and line.count("found") > 0: return False
        if line.count("You tipped") > 0 and line.count("players!") > 0: return False
        if line.count("found a") > 0 and line.count("Mystery Box!") > 0: return False
        if line.count("Watchdog has banned") > 0 and line.count("players in the last") > 0: return False
        if line.count("Staff have banned an additional") > 0 and line.count("in the last") > 0: return False
        return True

    def file(self, type: str, message: str, printLine = True):
        """Print and log a message

        Args:
            type (str): The type of event
            message (str): The message to display
            printLine (bool): If true, prints the line
        """
        message = "[{}] {} | {}: {}".format(
            
            (6-len(str(self.lineNumber))) * "0" + str(self.lineNumber),
            self.status + (GS.maxStatusLength - len(self.status)) * " ",
            type + (CE.maxEventLength - len(type)) * " ",
            message
        )
        message = message if len(message) < 150 else message[:150].strip() + " (...)"
        
        if printLine and (CE.printAll or type in CE.printTypes): print(message)
        if CE.logAll or type in CE.logTypes: open(self.combinedLog, "a").write(message + "\n")
        