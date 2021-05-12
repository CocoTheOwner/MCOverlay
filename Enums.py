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