class ChatEvents:

    # Non-useful
    uncharted = "Unch"
    removed = "Remv"
    useless = "Usles"

    # Useful & system
    quit = "Quit"
    join = "Join"
    lobby = "Lobby"
    who = "/who"
    player = "Enter"
    game = "Game"
    time = "Time"
    api = "API"
    party = "Party"
    afk = "AFK"
    bug = "BUG"

    # Useful
    chat = "Chat"
    void = "Void"
    bed = "Bed"
    eliminated = "Elim"
    died = "Death"

    # Macros
    all = "All"
    none = []

    useful = [
        quit,
        join,
        chat,
        lobby,
        who,
        player,
        game,
        time,
        api,
        void,
        bed,
        eliminated,
        party,
        died,
        afk,
        bug
    ]
    system = [
        quit,
        join,
        lobby,
        who,
        player,
        game,
        time,
        api,
        party,
        afk,
        bug
    ]

    maxEventLength = len(lobby)

    printTypes = useful
    logTypes = all

    printAll = printTypes == all
    logAll = logTypes == all

class GameStatus:
    inGame = "In Game"
    gameLobby = "Game Lobby"
    mainLobby = "Main Lobby"
    afterGame = "After Game"
    unknown = "Unknown"
    afk = "AFK"
    maxStatusLength = len(gameLobby)

class GameOrigin:
    mainLobby = "Main Lobby"
    gameLobby = "Game Lobby"
    mainChat = "Main Chat"
    gameChat = "Game Chat"
    party = "Party"

class SystemEvents:
    command = "Cmd"
    notify = "Note"
    api = "API"
    error = "Error"
    maxEventLength = ChatEvents.maxEventLength

class SystemStatus:
    startup = "Startup"
    waiting = "Waiting"
    running = "Running"
    shutdown = "Shutdown"
    oldLogs = "Old Logs"
    none = "None"
    maxStatusLength = GameStatus.maxStatusLength
class CommandOrigin:
    startup = "Startup"
    autowho = "Auto Who"
    autoleave = "Auto Leave"
    autoplist = "Auto P List"
    autoinvite = "Auto Invite"
    partyleft = "Party Member Left"
    partymissing = "Party Member Missing"

class PlayerTags:
    party = ["P", "Party"]
    guild = ["G", "Guild"]
    nick = ["N", "Nick"]
    alt = ["A", "Alt"]

class GameOptions:
    games = [
        "Arcade",
        "Arena",
        "Battleground",
        "HungerGames",
        "MCGO",
        "Paintball",
        "Quake",
        "TNTGames",
        "UHC",
        "VampireZ",
        "Walls",
        "Walls3",
        "GingerBread",
        "SkyWars",
        "TrueCombat",
        "SkyClash",
        "BuildBattle",
        "MurderMystery",
        "Bedwars",
        "Legacy",
        "Duels",
        "Pit",
        "SkyBlock",
        "SuperSmash",
        "SpeedUHC"
    ]

class Statistics:
    HypixelLevel = 0
    Tags = {}
    for tag in dir(PlayerTags):
        Tags[tag] = False
    BedwarsStats = {
        "Kills": False,
        "Deaths": False,
        "BedB": False,
        "BedL": False,
        "Finals": False,
        "Wins": False,
        "Losses": False,
        "Streak": False,
        "Iron": False,
        "Gold": False,
        "Diamonds": False,
        "Emerals": False,
        "Resources": False,
        "FKDR": False,
        "Kill/Death": False,
        "BedB/BedL": False,
        "Kill/Game": False,
        "BedB/Game": False,
        "BedL/Game": False,
        "Finals/Game": False,
        "Win/Loss": False,
    }
    Statistics = {
        "Bedwars": {
            "Stars": False,
            "Index": False, # = stars * FKDR ^ 2
            "Overall": BedwarsStats,
            "Solo": BedwarsStats,
            "Duo": BedwarsStats,
            "3s": BedwarsStats,
            "4s": BedwarsStats,
            "4v4": BedwarsStats
        },
        "BedwarsDreams": {
            "Stars": False,
            "Index": False,
            "Overall": BedwarsStats,
            "Rush": {
                "Duo": BedwarsStats,
                "4s": BedwarsStats,
                "Overall": BedwarsStats
            },
            "Ultimate": {
                "Duo": BedwarsStats + {"Kit": False},
                "4s": BedwarsStats + {"Kit": False},
                "Overall": BedwarsStats + {"Kit": False}
            },
            "Lucky": {
                "Duo": BedwarsStats,
                "4s": BedwarsStats,
                "Overall": BedwarsStats,
            },
            "Armed": {
                "Duo": BedwarsStats,
                "4s": BedwarsStats,
                "Overall": BedwarsStats
            },
            "Voidless": {
                "Duo": BedwarsStats,
                "4s": BedwarsStats,
                "Overall": BedwarsStats
            },
            "Castle": BedwarsStats
        }
    }