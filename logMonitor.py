
import os.path
from types import prepare_class
class logMonitor:
    path = ""
    mtime = 0
    linenumber = 0
    debug = False

    def __init__(self, path, debug = False):
        self.path = path
        self.debug = debug

    def tick(self):
        # Updates queue
        if (self.mtime != os.path.getmtime(self.path)):
            self.mtime = os.path.getmtime(self.path)
            self.readlog()

    def readlog(self):
        # Stores content of file
        content = ""

        # Retrieve content of file
        with open(self.path, "r") as f:
            content = f.read()

        # Splits the content into lines
        if (self.linenumber == 0):
            content = content.splitlines()
        else:
            content = content.splitlines()[self.linenumber + 1:content.count("\n") + 1]
        if len(content) != 0:

            # Loops over all lines in reversed order
            for line in content:

                # Add one to linecounter
                self.linenumber += 1

                # Process the line
                self.cleanLine(line)

    def cleanLine(self, line):
        # Make sure line is useful (very lightweight)
        if (not line.startswith("[")):
            return

        # (somewhat heavier)
        if (line.find("[Client thread/INFO]: [CHAT]") == -1):
            return

        # (quite heavy)
        info = line.strip().split("[Client thread/INFO]: [CHAT]")[1].strip()

        # (very light)
        if (info == ""):
            return

        # (quite heavy)
        if (self.debug): print("Line: " + info)

        # (quite light)
        self.process(info)

    playerQueue = {}
    # Process a line to retrieve available information
    def process(self, line: str):
        if (line.count("joined the lobby!") > 0):
            self.playerQueue[line.split("joined the lobby!")[0].split(" ")[-1]] = self.getRank(line)

        elif (line.count("has joined") > 0):
            self.playerQueue[line.split(" ")[0]] = self.getRank(line)

        else:
            # Checking for lobby-sent chat
            line = line.split(" ")[0].__contains__("[")
            return

    
    def getRank(line: str):
        if (line.__contains__(" [VIP] ")):
            return "VIP"
        if (line.__contains__(" [VIP+] ")):
            return "VIP+"
        if (line.__contains__(" [MVP] ")):
            return "MVP"
        if (line.__contains__(" [MVP+] ")):
            return "MVP+"
        if (line.__contains__(" [MVP++] ")):
            return "MVP++"
        return "NON"
            
    


