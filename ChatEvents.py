class ChatEvents:
    uncharted = "Unch"
    removed = "Remv"
    quit = "Quit"
    join = "Join"
    chat = "Chat"
    lobby = "Lobby"
    who = "/who"
    player = "Enter"
    game = "Game"
    time = "Time"
    api = "API"
    void = "Void"
    bed = "Bed"
    eliminated = "Elim"
    party = "Party"
    died = "Death"
    afk = "AFK"
    all = None
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