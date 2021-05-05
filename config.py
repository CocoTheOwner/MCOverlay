import json
from os import path
import os
class Config:
    configFile = "./config.txt"
    defaultConfig = {}
    config = {}
    def __init__(self, path, config):
        self.defaultConfig = config
        self.configFile = path
        self.ensureFileExistNotEmpty()
        self.load()
        self.ensureFileValid()

    def get(self, item):
        return self.config[item]
        
    def set(self, item, value):
        self.config[item] = value

    def getAll(self):
        keys = []
        for key in self.config:
            keys.append(key)
        return keys

    def load(self):
        with open(self.configFile, 'r') as f:
            self.config = json.load(f)

    def save(self):
        with open(self.configFile, 'w') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    def ensureFileExistNotEmpty(self):
        print(os.path.getsize(self.configFile))
        if (not os.path.isfile(self.configFile)):
            print("Making new config file at: " + self.configFile)
            with open(self.configFile, "w") as f:
                json.dump(self.defaultConfig, f, ensure_ascii=False, indent=4)
        elif (os.path.getsize(self.configFile) == 0):
            print("Filling existing but empty config file at: " + self.configFile)
            with open(self.configFile, "w") as f:
                json.dump(self.defaultConfig, f, ensure_ascii=False, indent=4)
    
    def ensureFileValid(self):
        for key in self.defaultConfig:
            if (not key in self.config):
                print("Key not found: " + key + " in keys: " + str(self.config))
                print("Invalid configuration file, does not contain all required keys! Resetting")
                with open(self.configFile.replace(".txt", "-invalid.txt"), "w") as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=4)
                with open(self.configFile, "w") as f:
                    json.dump(self.defaultConfig, f, ensure_ascii=False, indent=4)
                break
