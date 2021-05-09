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
    all = None
    none = []

    maxEventLength = len(lobby)

    printTypes = none
    logTypes = all

    printAll = printTypes == all
    logAll = logTypes == all

class GameStatus:
    inGame = "InGame"
    gameLobby = "GameLobby"
    mainLobby = "MainLobby"
    unknown = "Unknown"
    maxStatusLength = len(gameLobby)