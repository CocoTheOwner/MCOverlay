from pynput.keyboard import Key, Controller
import pyperclip
import time
class CommandSender:

    available = True
    controller = None
    def __init__(self):
        self.controller = Controller()

    def plist(self, origin: str):
        """Sends a p list command

        Args:
            origin (str): The origin of the command

        Returns:
            Command information which should be printed
        """
        return self.type("/p list", origin)

    def who(self, origin: str):
        """Sends a who command

        Args:
            origin (str): The origin of the command

        Returns:
            Command information which should be printed
        """
        return self.type("/who", origin)
        
    def leave(self, origin: str):
        """Sends a leave command

        Args:
            origin (str): The origin of the command

        Returns:
            Command information which should be printed
        """
        return self.type("/l", origin)
        
    def pwarp(self, origin: str):
        """Sends a p warp command

        Args:
            origin (str): The origin of the command

        Returns:
            Command information which should be printed
        """
        return self.type("/p warp", origin)

    def pleave(self, origin: str):
        """Leaves and warps the party after

        Args:
            origin (str): The origin of the command

        Returns:
            Command information which should be printed
        """
        self.leave(origin)
        time.sleep(0.5)
        self.pwarp(origin)
        return "Sent commands ({}): /l and /p warp".format(origin)

    def type(self, line: str, origin: str):
        """Writes a line using the virtual keyboard

        Args:
            line (str): The line to write
            origin (str): The origin of the command

        Returns:
            Command information which should be printed
        """
        if self.available:
            pyperclip.copy(line)
            self.controller.press(Key.enter)
            time.sleep(0.05)
            self.controller.release(Key.enter)
            self.controller.release(Key.shift)
            self.controller.press("t")
            self.controller.release("t")
            time.sleep(0.1)
            self.controller.press(Key.ctrl)
            self.controller.press("v")
            time.sleep(0.05)
            self.controller.release(Key.ctrl)
            self.controller.release("v")
            time.sleep(0.1)
            self.controller.press(Key.enter)
            self.controller.release(Key.enter)
            return "Sent command ({}): {}".format(origin, line)
        return "Command sender unavailable (command: {} from {})".format(line, origin)