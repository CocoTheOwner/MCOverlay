import os.path
from types import prepare_class
class logMonitor:
    path = ""
    mtime = 0
    linenumber = 0
    debug = False
    queue = []

    def __init__(self, path, debug = False):
        self.path = path
        self.debug = debug

    def tick(self):
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
                self.processLine(line)

    def processLine(self, line):
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
        self.queue.append(info)
