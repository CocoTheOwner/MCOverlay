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
        afk
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
        afk
    ]

    maxEventLength = len(lobby)

    printTypes = useful
    logTypes = all

    printAll = printTypes == all
    logAll = logTypes == all

class GameStatus:
    inGame = "InGame"
    gameLobby = "GameLobby"
    mainLobby = "MainLobby"
    unknown = "Unknown"
    afk = "AFK"
    maxStatusLength = len(gameLobby)