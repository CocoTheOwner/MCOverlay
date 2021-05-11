class PlayerQueue:
    queue = {}
    empty = True

    def get(self):
        """Retrieves all players currently in the queue and clears the queue

        Returns:
            dict: Contains all queued players
        
        """
        q = self.queue.copy()
        self.queue = {}
        self.empty = True
        return q

    def updateEmpty(self):
        """Updates the empty variable based on amount of queued players
        """
        self.empty = len(self.queue) == 0

    def delete(self, name: str):
        """Removes the player by given argument from the playerqueue

        Args:
            name (str): Name of the player to remove
        
        """
        for i,element in enumerate(self.queue):
            if element[0] == name:
                del self.queue[i]
        self.updateEmpty()

    def add(self, name: str, rank = "UNK", stars = -1, origin = "UNK"):
        """Adds a player to the playerqueue by name, rank and stars

        Args:
            name (str): The name of the player
            rank (str): The rank of the player
            stars (int): The amount of stars for the player
        """
        if not name in self.queue:
            self.queue[name] = {"rank": rank, "stars": stars, "origin": stars}
        else:
            info = self.queue[name]
            savedRank = info.get("rank")
            savedStars = info.get("stars")
            savedOrigin = info.get("origin")
            info = {
                "rank": (rank if rank != "UNK" else savedRank),
                "stars": (stars if stars != -1 else savedStars),
                "origin": (origin if origin != "UNK" else savedOrigin)
            }
        self.updateEmpty()

    def reset(self):
        """Resets the list maintained
        """
        self.queue = {}
        self.updateEmpty()