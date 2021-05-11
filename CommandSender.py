from pynput.keyboard import Key, Controller
import pyperclip
import time
controller = Controller()
class CommandSender:

    def plist(origin: str):
        """Sends a p list command

        Args:
            origin (str): The origin of the command

        Returns:
            Command information which should be printed
        """
        return CommandSender.type("/p list", origin)

    def who(origin: str):
        """Sends a who command

        Args:
            origin (str): The origin of the command

        Returns:
            Command information which should be printed
        """
        return CommandSender.type("/who", origin)
        
    def leave(origin: str):
        """Sends a leave command

        Args:
            origin (str): The origin of the command

        Returns:
            Command information which should be printed
        """
        return CommandSender.type("/l", origin)
        
    def pwarp(origin: str):
        """Sends a p warp command

        Args:
            origin (str): The origin of the command

        Returns:
            Command information which should be printed
        """
        return CommandSender.type("/p warp", origin)

    def pleave(origin: str):
        """Leaves and warps the party after

        Args:
            origin (str): The origin of the command

        Returns:
            Command information which should be printed
        """
        CommandSender.leave(origin)
        time.sleep(0.5)
        CommandSender.pwarp(origin)
        return "Sent commands ({}): /l and /p warp".format(origin)

    def type(line: str, origin: str):
        """Writes a line using the virtual keyboard

        Args:
            line (str): The line to write
            origin (str): The origin of the command

        Returns:
            Command information which should be printed
        """
        pyperclip.copy(line)
        controller.press(Key.enter)
        time.sleep(0.05)
        controller.release(Key.enter)
        controller.release(Key.shift)
        controller.press("t")
        controller.release("t")
        time.sleep(0.1)
        controller.press(Key.ctrl)
        controller.press("v")
        time.sleep(0.05)
        controller.release(Key.ctrl)
        controller.release("v")
        time.sleep(0.1)
        controller.press(Key.enter)
        controller.release(Key.enter)
        return "Sent command ({}): {}".format(origin, line)