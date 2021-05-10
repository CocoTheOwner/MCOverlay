from pynput import keyboard
from pynput.keyboard import Key, Controller
import time
controller = Controller()
class CommandSender:
    def who():
        """Sends a who command
        """
        CommandSender.type("/who")
        
    def leave():
        """Sends a leave command
        """
        CommandSender.type("/l")
        
    def pwarp():
        """Sends a p warp command
        """
        CommandSender.type("/p warp")

    def type(line: str):
        """Writes a line using the virtual keyboard

        Args:
            line (str): The line to write
        """
        controller.release(Key.shift)
        controller.press("t")
        controller.release("t")
        time.sleep(0.05)
        for character in line:
            controller.press(character)
            controller.release(character)
            time.sleep(0.01)
        controller.press(Key.enter)
        controller.release(Key.enter)