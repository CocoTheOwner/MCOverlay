import os
from time import thread_time
from Enums import ChatEvents as CE, GameStatus as GS, GameOrigin as GO, SystemStatus as SS
from PlayerQueue import PlayerQueue
class LogMonitor:

    combinedLog = "./logs/combined.txt"    
    if not os.path.exists("/".join(combinedLog.split("/")[:-1])):
        os.makedirs("/".join(combinedLog.split("/")[:-1]))
    open(combinedLog, "w").close() # Reset file

    # Do not break anything if not reset
    isPartyLeader = None
    lobbyName = None
    ownUsername = None
    newToken = None
    debug = None

    resetStats = False

    modificationTime = 0
    lineNumber = 0
    lobbyCap = 0
    timeLeftEstimate = 0

    toxicMessages = {
        "trash": "You lost to trash!",
        "bad": "You lost to bad players!",
        "gay": "You lost to gays!",
        "suck": "You lost to players that suck!"
    }

    status = GS.unknown

    # Must be reset after reading old logs
    toxicReaction = None

    autoWho = False
    autoLeave = False
    autoPartyList = False
    autoLeavePartyLeave = False
    partyMemberMissing = False
    partyMemberMissingTwo = False
    isStartup = False

    autoInvite = []
    failedWho = []
    game = []
    party = []

    queue = PlayerQueue()
    left = PlayerQueue()

    def __init__(self, logFilePath: str, ownUsername, debug = False):
        self.logFilePath = logFilePath
        self.ownUsername = ownUsername
        self.debug = debug

    def resetExposed(self):
        self.autoWho = False
        self.autoLeave = False
        self.autoLeavePartyLeave = False
        self.resetStats = False
        self.autoPartyList = False
        self.partyMemberMissing = False
        self.partyMemberMissingTwo = False
        self.toxicReaction = None
        self.autoInvite.clear()
        self.failedWho.clear()
        self.game.clear()
        self.party.clear()
        self.left.reset()
        self.queue.reset()

    def tick(self, isStartup = False):
        """Ticks the logger. Only ticks if there is a log change.
        """
        self.isStartup = isStartup
        if not os.path.exists(self.logFilePath): 
            self.file(CE.error, "Log file non-existant! Did you restart?")
            self.file(CE.error, "If so, ignore this. If you did not, please re-select the log file")
            return
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
            if self.debug: self.file(CE.system, "Reset linenumber. Likely due to Minecraft restarting.")
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
        if line.startswith("ONLINE:"):
            self.whoCommand(line)
        elif line.startswith("Party Leader: "):
            self.partyLeader(line)
        elif line.startswith("Members: ") or line.startswith("Party Members: ") or line.startswith("Party Moderators: "):
            self.partyMembers(line)
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
        elif line.endswith(" joined the party."):
            self.partyJoin(line)
        elif line.endswith(" left the party."):
            self.partyLeave(line)
        elif line.endswith(" has been kicked from the party"):
            self.partyKick(line)
        elif line.startswith("You have been kicked from the party by "):
            self.partyGotKicked(line)
        elif line == "The party was disbanded because all invites expired and the party was empty" or line.endswith(" has disbanded the party!"):
            self.partyDisbanded(line)
        elif line.count(" has promoted" ) > 0 and line.endswith("to Party Leader"):
            self.partyPromote(line)
        elif line.startswith("The party was transferred to "):
            self.partyTransfer(line)
        elif line == "Bed Wars":
            self.endGameBedwars()
        elif line.count("joined the lobby!") > 0:
            self.joinLobby(line)
        elif line.count("has joined") > 0:
            self.playerJoinGame(line)
        elif line.endswith(" reconnected."):
            self.playerRejoinGame(line)
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
            self.chat(line)
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
        """

        if self.status == GS.inGame or self.status == GS.afterGame:
            self.gameChatMessage(line)
            return

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
        if user == self.ownUsername:
            self.file(CE.chat, "[{}] {}{}: {}".format(stars, rank, user, message.strip()))
            return

        # Add the player to the playerqueue
        self.queue.add(user, rank, stars, GO.mainChat)

        rank = "[" + rank + "] " if rank != "NON" else ""

        for word in message.strip().split(" "):
            if word.count(self.ownUsername) > 0:
                # This word mentions one of the main users' usernames, invite this player!
                if not user in self.party: self.autoInvite.append(user)


        self.file(CE.chat, "[{}] {}{}: {}".format(stars, rank, user, message.strip()))
    
    def gameChatMessage(self, line: str):
        """Process a game chat event

        Args:
            line (str): Line to process

        Examples:
            username: message may contain spaces
            [RANK] username: message may contain spaces
        """
        split = line.split(" ")

        # Retrieve rank, username and message
        if split[0].endswith(":"):
            rank = "NON"
            user = split[0].removesuffix(":")
            message = " ".join(split[1:])
        else:
            rank = LogMonitor.getRank(split[0])
            user = split[1].removesuffix(":")
            message = " ".join(split[2:])

        # Clean the message
        while (message.count("  ") > 0):
            message = message.replace("  ", " ")

        # Check if the player is the main player
        if user == self.ownUsername:
            rank = ""
        else:
            rank = "[" + rank + "] " if rank != "NON" else ""

        if (message.count("/who") > 0 and message.count(" ") < 2 or message.count("who") > 0 and message.count(" ") == 0)\
            and self.status == GS.gameLobby:
            if user == self.ownUsername:
                self.autoWho = True
                self.file(CE.chat, "You failed an autowho! Sending again...")
            else:
                self.failedWho.append(user)
                self.file(CE.chat, "{}{} failed /who: {}".format(rank, user, message.strip()))
        else:
            self.file(CE.chat, "{}{}: {}".format(rank, user, message.strip()))

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

        # Retrieve the lobby name
        name = line.removeprefix("You are currently connected to server").removeprefix("Sending you to").removeprefix("Taking you to").removesuffix("!").strip().split(' ')[0]

        # Set the lobby name if changed
        if name != self.lobbyName:

            # Reset the lobby counter
            self.timeLeftEstimate = 0

            self.file(CE.lobby, "[{}] -> [{}]".format(self.lobbyName, name))

            # Set the lobby name
            self.lobbyName = name

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

        if not name == self.ownUsername:
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

        if name != self.ownUsername:
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
        self.timeLeftEstimate = 0

        line = line.removeprefix(">>>").removesuffix("joined the lobby!").strip().split(" ")
        # ["[RANK]", "username"]

        rank = LogMonitor.getRank(line[0])
        rank = "[" + rank + "] " if rank != "NON" else ""
        name = line[1]

        if name == self.ownUsername:
            return

        self.queue.add(name, rank, origin=GO.mainLobby)


        self.file(CE.player, "{}{}".format(rank, name))

    def teamEliminated(self, line:str):
        """Process a team eliminated event

        Args:
            line (str): Line to process

        Example:
            TEAM ELIMINATED > Color Team has been eliminated!
        """
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
        if self.status == GS.gameLobby and self.timeLeftEstimate > 5:
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

        if name1 == self.ownUsername:
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
        if name == self.ownUsername:
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
        x = line.removeprefix("Party ").removeprefix("Members: ").removeprefix("Moderators: ").split(" ? ")
        for playerWithRank in x:
            playerWithRank = playerWithRank.split(" ")
            rank = LogMonitor.getRank(playerWithRank[0])
            if rank == "NON":
                name = playerWithRank[0]
            else:
                name = playerWithRank[1]
            if not name in self.party:
                self.party.append(name)
            self.queue.add(name, rank, origin=GO.party)

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

        self.party.clear()

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

        self.queue.add(name, rank, origin=GO.party)

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
            self.party.clear()
            return
        x = LogMonitor.getRank(line.split(" ")[0])
        if x == "NON":
            name = x
            rank = ""
        else:
            name = line.split(" ")[1]
            rank = "[" + x + "] "

        if not name in self.party:
            self.file(CE.bug, "Someone left the party that was not in it?! BUG!")
            self.autoPartyList = True
        else:
            self.party.remove(name)

        self.file(CE.party, "{}{} left the party".format(rank, name))
        self.file(CE.party, ("Party members are now: {}".format(", ".join(self.party))) if len(self.party) > 0 else "The party is empty!")

    def partyKick(self, line: str):
        """ Processes a party kick event

        Args:
            line (str): The line to process

        Example
            [RANK] username
            username has been kicked from the party
        """
        x = line.removesuffix(" has been kicked from the party").split(" ")
        rank = LogMonitor.getRank(x[0])
        if rank == "NON":
            name = x[0]
            rank = ""
        else:
            name = x[1]
            rank = "[" + rank + "] "
        if name not in self.party:
            self.file(CE.party, "{}{} has been kicked from the party but was not in it!".format(rank, name))
        else:
            self.party.remove(name)
            self.file(CE.party, "{}{} has been kicked from the party".format(rank, name))

    def partyGotKicked(self, line: str):
        """ Processes a party got kicked event

        Args:
            line (str): The line to process

        Example
            You have been kicked from the party by [RANK] username
            You have been kicked from the party by username
        """
        self.isPartyLeader = None
        self.party.clear()
        self.autoPartyList = False
        self.autoLeavePartyLeave = False
        self.partyMemberMissing = False
        self.partyMemberMissingTwo = False
        x = line.removeprefix("You have been kicked from the party ").split(" ")
        rank = LogMonitor.getRank(x[0])
        if rank == "NON":
            name = x[0]
            rank = ""
        else:
            name = x[1]
            rank = "[" + rank + "] "
        self.file(CE.party, "{}{} kicked you from the party".format(rank, name))

    def partyDisbanded(self, line: str):
        """Process a party disband

        Args
            line (str): Line to process
        
        Example:
            The party was disbanded because all invites expired and the party was empty
            [RANK] username has disbanded the party!
            username has disbanded the party!
        """
        self.isPartyLeader = None
        self.party.clear()
        self.autoPartyList = False
        self.autoLeavePartyLeave = False
        self.partyMemberMissing = False
        self.partyMemberMissingTwo = False
        if line.endswith("has disbanded the party!"):
            x = line.removesuffix("has disbanded the party!").strip().split(" ")
            rank = LogMonitor.getRank(x[0])
            if rank == "NON":
                name = x[0]
                rank = ""
            else:
                name = x[1]
                rank = "[" + rank + "] "
            self.file(CE.party, "{}{} has disbanded the party".format(rank, name))
        else:
            self.file(CE.party, "The party was disbanded")

    def partyPromote(self, line: str):
        """Process a party promote

        Args:
            line (str): Line to process

        Example:
            [RANK] name1 has promoted [RANK] name2 to Party Leader
            name1 has promoted name2 to Party Leader
        """
        x = line.replace(" has promoted", "").removesuffix(" to Party Leader").split(" ")
        if x[-1] == self.ownUsername:
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

        if name1 == self.ownUsername:
            rank1 = ""
            name1 = "You"
        if name2 == self.ownUsername:
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
        if x[-2] == self.ownUsername:
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

        if name1 == self.ownUsername:
            rank1 = ""
            name1 = "you"
        if name2 == self.ownUsername:
            rank2 = ""
            name2 = "you"

        self.file(CE.party, "{}{} transferred the party to {}{}".format(rank1, name1, rank2, name2))

    def endGameBedwars(self):
        """Process a game end event for bedwars games

        Example:
            "Bed Wars"

        Status:
            Based on current status type, switches to:
            MainLobby (if in game)
            InGame (if in lobby)
        """
        if self.status == GS.inGame:
            self.status = GS.afterGame
            self.autoWho = False
            self.autoLeave = True
            self.resetStats = True
            self.game.clear()
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
        lobbyCap = int(x[1])

        # Store player by username
        self.queue.add(name, origin=GO.gameLobby)
        self.game.append(name)

        if not len(self.game) == int(x[0]):
            self.autoWho = True
            if len(self.game) > int(x[0]):
                self.game.clear()
        elif name == self.ownUsername and int(x[0]) > 1:
            self.autoWho = True

        # Save the amount of players in the lobby
        self.lobbyCap = lobbyCap

        self.file(CE.join, "{} ({}/{})".format(name, len(self.game), lobbyCap))
        if self.debug: self.file(CE.join, "Currently in lobby ({}/{}): {}".format(len(self.game), self.lobbyCap, ", ".join(self.game)))

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
        self.resetStats = True
        self.game.clear()
        for username in line:
            self.file(CE.who, username)
            self.queue.add(username, origin=GO.gameLobby)
            self.game.append(username)
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
        """

        # Remove one player from the lobby count

        # Remove the player from the queue
        name = line.removesuffix(" has quit!").removesuffix("disconnected").strip()
        self.queue.delete(name)
        self.left.add(name, "UNK", -1)
        if name in self.game:
            self.game.remove(name)
        else:
            self.file(CE.lobby, "{} left but were not in the game! BUG?!".format(name))
            self.file(CE.lobby, "Currently in game: {}".format(", ".join(self.game)))

        self.file(CE.quit, "{} ({}/{})".format(name, len(self.game), self.lobbyCap))

        if name == self.ownUsername:
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

        time = int(line.removeprefix("The game starts in").removesuffix("!").removesuffix("s").removesuffix("second").strip())
        self.timeLeftEstimate = time
        if self.timeLeftEstimate > 3:
            for player in self.party:
                if not player in self.game:
                    self.file(CE.lobby, "Party member missing: {} | Game: {}".format(player, ", ".join(self.game)))
                    if self.partyMemberMissing:
                        self.partyMemberMissingTwo = True
                    else:
                        self.partyMemberMissing = True
                        self.autoWho = True

        self.file(CE.time, str(time) + "s")

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

    def chat(self, line: str):
        """Process a line with a colon.
        Likely chat, but unsure.

        Args:
            line (str): The line to process
        """
        if self.status == GS.mainLobby and line.startswith("[") and line.split(" ")[0].endswith("?]") and (line.split(" ")[1].endswith(":") or line.split(" ")[2].endswith(":")):
            self.lobbyChatMessage(line)
        elif self.status == GS.inGame or self.status == GS.gameLobby:
            self.gameChatMessage(line)
        elif self.status == GS.afterGame:
            self.afterGameChat(line)
        self.potentialChat(line)

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
        line = line.split(" ")
        if len(line) < 3: self.unprocessed(" ".join(line))
        rank = LogMonitor.getRank(line[0])
        name = line[0] if rank == "NON" else line[1]
        message = " ".join(line[(1 if rank == "NON" else 2):])

        if not name.endswith(":"):
            self.unprocessed(" ".join(line))
        else:
            self.file(CE.chat, "{}{}: {}".format("[" + rank + "] " if rank != "NON" else "", name.removesuffix(":"), message))

    def afterGameChat(self, line: str):
        """Process a potential after game toxic message

        Args:
            line (str): Line to process

        Examples:
            username: You are trash
            username: You are gay
            username: You are bad
            Etc...

        Status:
            afterGame (should already be set, will not be set here)
        """
        split = line.split(" ")
        user = split[0].removesuffix(":")
        message = " ".join(split[1:])

        # Clean the message
        while (message.count("  ") > 0):
            message = message.replace("  ", " ")

        # Check if the player is the main player
        for word in message.split(" "):
            if word.lower() in self.toxicMessages.keys():
                self.toxicReaction = self.toxicMessages[word.lower()]
                self.file(CE.toxic, "Toxic message by {}: {}".format(user, message.replace(word, word.upper())))
                return
        self.potentialChat(line)

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
        line == "send:lobby" or

        line.replace("?","") == "" or
        line.replace("-","") == "" or
        len(line.replace("-","").strip().replace("(","").replace(")","")) == 1 or

        line.startswith("You will respawn in") or
        line.startswith("Automatically activated:") or 
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
        line.count("Staff have banned an additional") > 0 and line.count("in the last") > 0 or
       (line.count(":") > 0 and (line.split(" ")) == 0)
        )

    def file(self, type: str, message: str, printLine = True):
        """Print and log a message

        Args:
            type (str): The type of event
            message (str): The message to display
            printLine (bool): If true, prints the line
        """
        if not self.isStartup:
            message = "[{}] {} | {}: {}".format(
                
                (6-len(str(self.lineNumber))) * "0" + str(self.lineNumber),
                self.status + (GS.maxStatusLength - len(self.status)) * " ",
                type + (CE.maxEventLength - len(type)) * " ",
                message
            )
        else:
            message = "[{}] {} | {}: {}".format(
                
                "SYSTEM",
                SS.oldLogs + (GS.maxStatusLength - len(SS.oldLogs)) * " ",
                "Prevs" + (CE.maxEventLength - len("Prevs")) * " ",
                message
            )
        message = message if len(message) < 150 else message[:150].strip() + " (...)"
        
        if printLine and (CE.printAll or type in CE.printTypes): 
            print(message)
        if CE.logAll or type in CE.logTypes: 
            open(self.combinedLog, "a").write(message + "\n")
        