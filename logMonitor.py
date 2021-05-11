import os
from Enums import ChatEvents as CE, GameStatus as GS, Origin as OG
from PlayerQueue import PlayerQueue
class LogMonitor:

    combinedLog = "./logs/combined.txt"    
    if not os.path.exists("/".join(combinedLog.split("/")[:-1])):
        os.makedirs("/".join(combinedLog.split("/")[:-1]))
    open(combinedLog, "w").close() # Reset file

    isPartyLeader = None
    lobbyName = None
    mainUsers = None
    newToken = None
    debug = None

    modificationTime = 0
    lineNumber = 0
    playersInLobby = 0
    lobbyCap = 0

    autoWho = False
    autoLeave = False
    autoPartyList = False
    autoLeavePartyLeave = False


    resetStats = False

    autoInvite = []

    party = []

    status = GS.unknown

    queue = PlayerQueue()
    left = PlayerQueue()

    def __init__(self, logFilePath: str, mainUsers, debug = False):
        self.logFilePath = logFilePath
        self.mainUsers = mainUsers
        self.debug = debug

    def resetExposed(self):
        self.autoWho = False
        self.autoLeave = False
        self.autoLeavePartyLeave = False
        self.resetStats = False
        self.autoPartyList = False
        self.autoInvite = []
        self.left.reset()
        self.queue.reset()

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
                self.file(CE.useless, line, False)
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
            self.file(CE.removed, split)
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
        elif line.endswith("fell into the void."):
            self.voided(line)
        elif line.startswith("BED DESTRUCTION > "):
            self.bedDestroy(line)
        elif line.startswith("TEAM ELIMINATED > "):
            self.teamEliminated(line)
        elif line.endswith("has disconnected, they have 5 minutes to rejoin before they are removed from the party."):
            self.partyMemberLeft(line)
        elif line == "You have been eliminated!":
            self.selfDied()
        elif line.endswith(" to the party! They have 60 seconds to accept."):
            self.partyInvite(line)
        elif line.startswith("Party Leader: "):
            self.partyLeader(line)
        elif line.startswith("Party Members: "):
            self.partyMembers(line)
        elif line.endswith(" joined the party."):
            self.partyJoin(line)
        elif line.endswith(" left the party."):
            self.partyLeave(line)
        elif line.count(" has promoted" ) > 0 and line.endswith("to Party Leader"):
            self.partyPromote(line)
        elif line.startswith("The party was transferred to "):
            self.partyTransfer(line)
        elif line == "Bed Wars":
            self.endGame()
        elif line.count("joined the lobby!") > 0:
            self.joinLobby(line)
        elif line.count("has joined") > 0:
            self.playerJoinGame(line)
        elif line.endswith(" reconnected."):
            self.playerRejoinGame(line)
        elif line.startswith("ONLINE:"):
            self.whoCommand(line)
        elif line == "You are AFK. Move around to return from AFK.":
            self.afk()
        elif line.endswith("has quit!") or line.endswith("disconnected"):
            self.quitGame(line)
        elif line.startswith("The game starts in") and line.count("second") > 0:
            self.gameTime(line)
        elif line == "We don't have enough players! Start cancelled.":
            self.file("Game", "Start cancelled")
        elif line.startswith("Your new API key is "):
            self.newAPIKey(line)
        elif line.count(":") > 0:
            self.potentialChat(line)
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
        self.queue.add(user, rank, stars, OG.mainChat)

        rank = "[" + rank + "] " if rank != "NON" else ""

        for word in message.strip().split(" "):
            for player in self.mainUsers:
                if word.count(player) > 0:
                    # This word mentions one of the main users' usernames, invite this player!
                    self.autoInvite.append(user)


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
            self.lobbyName = name
            self.file(CE.lobby, "[{}] -> [{}]".format(self.lobbyName, name))

    def voided(self, line: str):
        """Process a fell in the void event

        Args:
            line (str): Line to process

        Example:
            username fell into the void.

        Status:
            inGame
        """
        self.status = GS.inGame

        name = line.replace("username fell into the void.", "").strip()

        if not name in self.mainUsers:
            # Do not process statistics (useless)
            self.file(CE.removed, line)
            
        else:
            self.file(CE.void, "You voided!")

    def bedDestroy(self, line: str):
        """Process a lobby join event

        Args:
            line (str): Line to process

        Example:
            BED DESTRUCTION > White Bed description username!

        Status:
            inGame
        """
        self.status = GS.inGame

        name = line.removeprefix("BED DESTRUCTION > ").removesuffix("!").split(" ")[-1]

        if name not in self.mainUsers:
            self.file(CE.removed, line)

        else:
            self.file(CE.bed, "You destroyed a bed!")

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

        self.queue.add(name, rank, origin=OG.mainLobby)


        self.file(CE.player, "{}{}".format(rank, name))

    def teamEliminated(self, line:str):
        """Process a team eliminated event

        Args:
            line (str): Line to process

        Example:
            TEAM ELIMINATED > Color Team has been eliminated!

        Status:
            inGame
        """
        self.status = GS.inGame
        team = line.removeprefix("TEAM ELIMINATED > ").removesuffix("has been eliminated!").strip()
        self.file(CE.eliminated, team + " eliminated!")
        

    def partyMemberLeft(self, line:str):
        """Process a party member leave event

        Args:
            line (str): Line to process

        Example:
            [RANK] username has disconnected, they have 5 minutes to rejoin before they are removed from the party.
            username has disconnected, they have 5 minutes to rejoin before they are removed from the party.

        Status:
            unchanged
        """
        x = line.removesuffix("has disconnected, they have 5 minutes to rejoin before they are removed from the party.").strip().split(" ")
        if self.status == GS.gameLobby:
            self.autoLeavePartyLeave = True
        if len(x) == 1:
            self.file(CE.party, "Your party member: " + x[0] + " disconnected!")
        else:
            self.file(CE.party, "Your party member: " + x[0] + " " + x[1] + " disconnected!")

    def selfDied(self):
        """Process player death

        Status:
            inGame
        """
        self.status = GS.inGame
        self.file(CE.died, "You died")
        

    def partyInvite(self, line:str):
        """Process a party invite

        Args:
            line (str): Line to process

        Example:
            [RANK] name1 invited [RANK] name2 to the party! They have 60 seconds to accept.
            [RANK] name1 invited name2 to the party! They have 60 seconds to accept.
            name1 invited [RANK] name2 to the party! They have 60 seconds to accept.
            name1 invited name2 to the party! They have 60 seconds to accept.
        """
        line = line.removesuffix(" to the party! They have 60 seconds to accept.").strip().split(" ")
        x = LogMonitor.getRank(line[0])
        if x == "NON":
            name1 = x
            rank1 = ""
        else:
            name1 = line[1]
            rank1 = "[" + x + "] "

        if name1 in self.mainUsers:
            name1 = "You"
            rank1 = ""

        name2 = line[-1]
        x = LogMonitor.getRank(line[-2])
        rank2 = "" if x == "NON" else "[" + x + "] "

        self.file(CE.party, "{}{} invited {}{}".format(rank1, name1, rank2, name2))

    def partyLeader(self, line: str):
        """Process a party list leader line

        Args:
            line (str): Line to process

        Example:
            Party Leader: [RANK] username ?
            Party Leader: username ?
        """

        x = line.removeprefix("Party Leader: ").split(" ")
        rank = LogMonitor.getRank(x[0])
        if rank == "NON":
            name = x[0]
            rank = ""
        else:
            name = x[1]
            rank = rank + " "
        if name in self.mainUsers:
            self.isPartyLeader = True
        
        self.file(CE.party, "Party List:")
        self.file(CE.party, "Leader: {}{}".format(rank, name))
        

    def partyMembers(self, line: str):
        """Process a party list member line

        Args:
            line (str): Line to process

        Example:
            Party Members: [RANK] username ? username ? [RANK] username
        """
        x = line.removeprefix("Party Members: ").split(" ? ")
        for playerWithRank in x:
            playerWithRank = playerWithRank.split(" ")
            rank = LogMonitor.getRank(playerWithRank[0])
            if rank == "NON":
                name = playerWithRank[0]
            else:
                name = playerWithRank[1]
            if not name in self.party:
                self.party.append(name)
            self.queue.add(name, rank, origin=OG.party)

        self.file(CE.party, "Members: {}".format(", ".join(self.party)))

    def partyDisband(self, line: str):
        """Process a party disband

        Args:
            line(str): Line to process

        Example:
            [RANK] username has disbanded the party!
            username has disbanded the party!

        """


        x = line.removesuffix(" has disbanded the party!").split(" ")
        rank = LogMonitor.getRank(x[0])
        if rank == "NON":
            name = x[0]
            rank = ""
        else:
            name = x[1]
            rank = rank + " "

        self.party = []

        self.isPartyLeader = None

        self.file(CE.party, "The party was disbanded by {}{}".format(rank, name))

    def partyJoin(self, line: str):
        """Process a party join

        Args:
            line (str): Line to process

        Example:
            [RANK] name1 joined the party.
            name1 joined the party.

        Status:
            unchanged
        """
        x = LogMonitor.getRank(line.split(" ")[0])
        if x == "NON":
            name = line.split(" ")[0]
            rank = ""
        else:
            name = line.split(" ")[1]
            rank = "[" + x + "] "

        self.party.append(name)

        self.queue.add(name, rank, origin=OG.party)

        if len(self.party) == 0:
            self.isPartyLeader = False

        self.file(CE.party, "{}{} joined the party".format(rank, name))
        self.file(CE.party, ("Party members are now: {}".format(", ".join(self.party))) if len(self.party) > 0 else "The party is empty!")

    def partyLeave(self, line: str):
        """Process a party leave

        Args:
            line (str): Line to process

        Example:
            [RANK] name1 left the party.
            name1 left the party.

        Status:
            unchanged
        """
        if line == "You left the party.":
            self.isPartyLeader = False
            self.party = []
            return
        x = LogMonitor.getRank(line.split(" ")[0])
        if x == "NON":
            name = x
            rank = ""
        else:
            name = line.split(" ")[1]
            rank = "[" + x + "] "

        if not name in self.party:
            print("Someone left the party that was not in it?! BUG!")
            self.autoPartyList = True
        else:
            self.party.remove(name)

        self.file(CE.party, "{}{} left the party".format(rank, name))
        self.file(CE.party, ("Party members are now: {}".format(", ".join(self.party))) if len(self.party) > 0 else "The party is empty!")

    def partyPromote(self, line: str):
        """Process a party promote

        Args:
            line (str): Line to process

        Example:
            [RANK] name1 has promoted [RANK] name2 to Party Leader
            name1 has promoted name2 to Party Leader
        """
        x = line.replace(" has promoted", "").removesuffix(" to Party Leader").split(" ")
        if x[-1] in self.mainUsers:
            self.isPartyLeader = True
        else:
            self.isPartyLeader = False
        rank1 = LogMonitor.getRank(x[0])
        if rank1 == "NON":
            rank1 = ""
            name1 = x[0]
        else:
            rank1 = "[" + rank1 + "] "
            name1 = x[1]
        
        rank2 = LogMonitor.getRank(x[-2])
        if rank2 == "NON":
            rank2 = ""
            name2 = x[-1]
        else:
            rank2 = "[" + rank2 + "] "
            name2 = x[-1]

        if name1 in self.mainUsers:
            rank1 = ""
            name1 = "You"
        if name2 in self.mainUsers:
            rank2 = ""
            name2 = "you"

        self.file(CE.party, "{}{} promoted {}{} to Party Leader".format(rank1, name1, rank2, name2))

    def partyTransfer(self, line: str):
        """Process a party transfer

        Args:
            line (str): Line to process

        Example:
            The party was transferred to [RANK] name1 by [RANK] name2
            The party was transferred to name1 by name2
        """
        x = line.removeprefix("The party was transferred to ").replace(" by", "").split(" ")
        if x[-2] in self.mainUsers:
            self.isPartyLeader = True
        else:
            self.isPartyLeader = False
        rank1 = LogMonitor.getRank(x[0])
        if rank1 == "NON":
            rank1 = ""
            name1 = x[0]
        else:
            rank1 = "[" + rank1 + "] "
            name1 = x[1]
        
        rank2 = LogMonitor.getRank(x[-2])
        if rank2 == "NON":
            rank2 = ""
            name2 = x[-1]
        else:
            rank2 = "[" + rank2 + "] "
            name2 = x[-1]

        if name1 in self.mainUsers:
            rank1 = ""
            name1 = "you"
        if name2 in self.mainUsers:
            rank2 = ""
            name2 = "you"

        self.file(CE.party, "{}{} transferred the party to {}{}".format(rank1, name1, rank2, name2))

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
            self.autoLeave = True
            self.resetStats = True
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
        x = line[-1].replace("(","").replace(")!","").split("/")
        joinNumber = int(x[0])
        lobbyCap = int(x[1])

        if name in self.mainUsers and joinNumber > 1:
                self.autoWho = True

        # Store player by username
        self.queue.add(name, origin=OG.gameLobby)

        # Save the amount of players in the lobby
        self.playersInLobby = joinNumber
        self.lobbyCap = lobbyCap

        self.file(CE.join, "{} ({}/{})".format(name, joinNumber, lobbyCap))

    def playerRejoinGame(self, line: str):
        """Process a player game lobby rejoin event

        Args:
            line (str): Line to process

        Example:
            username reconnected.

        Status:
            inGame
        """
        self.status = GS.inGame
        name = line.removesuffix(" reconnected.")
        self.file(CE.join, "{} rejoined".format(name))
    
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
        self.resetStats = True
        for username in line:
            self.file(CE.who, username)
            self.queue.add(username, origin=OG.gameLobby)
        self.file(CE.who, "({}/{}) players in the lobby".format(len(line), self.lobbyCap))

    def afk(self):
        """Process an afk event

        Args:
            line (str): Line to process

        Status:
            afk
        """
        self.status = GS.afk
        self.file(CE.afk, "You went AFK")

    def quitGame(self, line: str):
        """Process a game lobby quit event

        Args:
            line (str): Line to process

        Example:
            username has quit!
            username has disconnected

        Status:
            unchanged
        """

        # Remove one player from the lobby count
        self.playersInLobby -= 1

        # Remove the player from the queue
        name = line.removesuffix(" has quit!").removesuffix("disconnected").strip()
        self.queue.delete(name)
        self.left.add(name, "UNK", -1)

        self.file(CE.quit, "{} ({}/{})".format(name, self.playersInLobby, self.lobbyCap))

        if name in self.mainUsers:
            self.file(CE.lobby, "Left lobby [{}]".format(self.lobbyName))


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

        time = line.removeprefix("The game starts in").removesuffix("!").removesuffix("s").removesuffix("second").strip()

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

    def potentialChat(self, line: str):
        """Process a potential chat message

        Args:
            line (str): Line to process

        Examples:
            [RANK] username: message with spaces
            username: message with spaces

        Status:
            inGame
        """
        self.status = GS.inGame
        line = line.split(" ")
        if len(line) < 3: self.unprocessed(" ".join(line))
        rank = LogMonitor.getRank(line[0])
        name = line[0] if rank == "NON" else line[1]

        if not name.endswith(":"):
            self.unprocessed(" ".join(line))
        else:
            self.file(CE.chat, "{}{}: {}".format(rank + " " if rank != "NON" else "", name, " ".join(line[(1 if rank == "NON" else 2):])))

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
        return not (line == "" or
        line == "[WATCHDOG ANNOUNCEMENT]" or
        line == "This server is full! (Server closed)" or
        line == "A player has been removed from your lobby." or
        line == "You were kicked while joining that server!" or
        line == "Use /report to continue helping out the server!" or
        line == "Blacklisted modifications are a bannable offense!" or
        line == "You already have an API Key, are you sure you want to regenerate it?" or
        line == "If you get disconnected use /rejoin to join back in the game." or
        line == "You have respawned!" or
        line == "Protect your bed and destroy the enemy beds." or
        line == "Upgrade yourself and your team by collecting" or
        line == "Iron, Gold, Emerald and Diamond from generators" or
        line == "to access powerful upgrades." or
        line == "This game has been recorded. Click here to watch the Replay!" or
        line == "You cannot invite that player since they're not online." or

        line.replace("?","") == "" or
        line.replace("-","") == "" or
        len(line.replace("-","").strip().replace("(","").replace(")","")) == 1 or

        line.startswith("You will respawn in") or
       (line.startswith("+") and line.count("Bed Wars Experience (") > 0) or
       (line.startswith("+") and line.count("coins! (") > 0) or
       (line.startswith("+") and line.endswith("Iron")) or
       (line.startswith("+") and line.endswith("Gold")) or
        line.startswith("Guild > ") or
        line.startswith("Friend > ") or
        line.startswith("You don't have enough") or
        line.count("You purchased") > 0 or
        line.count("Unknown command. Type \"help\" for help.") > 0 or
        line.count("[Mystery Box]") > 0 and line.count("found") > 0 or
        line.count("You tipped") > 0 and line.count("players!") > 0 or
        line.count("found a") > 0 and line.count("Mystery Box!") > 0 or
        line.count("Watchdog has banned") > 0 and line.count("players in the last") > 0 or
        line.count("Staff have banned an additional") > 0 and line.count("in the last") > 0
        )

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
        