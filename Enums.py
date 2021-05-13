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
    error = "ERROR"
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
    arcade ="Arcade"
    arena = "Arena"
    battleground = "Battleground"
    hungergames = "HungerGames"
    mcgo = "MCGO"
    paintball = "Paintball"
    quake = "Quake"
    tntgames = "TNTGames"
    uhc = "UHC"
    vampirez = "VampireZ"
    walls = "Walls"
    walls3 = "Walls3"
    gingerbread = "GingerBread"
    skywars = "SkyWars"
    truecombat = "TrueCombat"
    skyclash = "SkyClash"
    buildbattle = "BuildBattle"
    murdermystery = "MurderMystery"
    bedwars = "Bedwars"
    legacy = "Legacy"
    duels = "Duels"
    pit = "Pit"
    skyblock = "SkyBlock"
    supersmash = "SuperSmash"
    speeduhc = "SpeedUHC"
    games = [
        arcade,
        arena,
        battleground,
        hungergames,
        mcgo,
        paintball,
        quake,
        tntgames,
        uhc,
        vampirez,
        walls,
        walls3,
        gingerbread,
        skywars,
        truecombat,
        skyclash,
        buildbattle,
        murdermystery,
        bedwars,
        legacy,
        duels,
        pit,
        skyblock,
        supersmash,
        speeduhc
    ]

class Bedwars:
    stats = {
        "winstreak": "Winstreak",
        "wins_bedwars": "Wins",
        "kills_bedwars": "Kills",
        "deaths_bedwars": "Deaths",
        "losses_bedwars": "Losses",
        "beds_lost_bedwars": "BedsL",
        "beds_broken_bedwars": "BedsB",
        "final_kills_bedwars": "FinalKs",
        "final_deaths_bedwars": "FinalDs",
        "games_played_bedwars": "Games"
    }
    modes = {
        "eight_two_rush": "DuoRush",
        "four_four_rush": "4sRush",
        "eight_two_ultimate": "DuoUlt",
        "four_four_ultimate": "4sUlt",
        "eight_two_lucky": "DuoLucky",
        "four_four_lucky": "4sLucky",
        "eight_two_armed": "DuoArmed",
        "four_four_armed": "4sArmed",
        "eight_two_voidless": "DuoVoidL",
        "four_four_voidless": "4sVoidL",
        "castle": "Castle",
        "eight_one": "Solo",
        "eight_two": "Duo",
        "four_three": "3s",
        "four_four": "4s",
        "two_four": "4v4"
    }