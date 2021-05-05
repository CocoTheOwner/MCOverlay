from collections import defaultdict
from config import Config
defaultConfig = {
    "ownUsers": [
        "username"
    ],
    "token": "token"
}
config = Config('./config.json', defaultConfig)
config.save()