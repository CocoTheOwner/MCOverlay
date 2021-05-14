# Import and initialize the pygame library
import pygame, os
from pygame import Color, Rect, Surface, display, mouse, draw, cursors, event as Event
from pygame.constants import *
pygame.init()

class MCOv2:

    # Version
    version = None

    # Cursor configurations
    # More @ https://www.pygame.org/docs/ref/cursors.html
    cursorOptions = [cursors.diamond, cursors.tri_left, cursors.tri_right, cursors.arrow]
    cursor = None

    # Display
    displayNumber = None
    # TODO: Add RESIZABLE here. Requires that all elements are properly scalable
    displayTags = SRCALPHA | SHOWN

    # Window
    screen = None
    running = False
    windowBackgroundColor = None
    windowSize = None
    windowPosition = None
    windowIsFocused = False
    windowHasMouse = False
    windowIsReceivingFile = False
    windowFullscreen = False
    windowVisible = True

    # Buttons
    mouseButtons = [False for _ in range(0,10)]
    mousePos = (0, 0)

    # Logfile
    logFile = None

    def __init__(
        self,
        width = 500,
        height = 500,
        windowPosition = (50, 50),
        background = Color(0,131,45,255),
        fullscreen = False,
        displayNumber = 0,
        cursor = 0,
        version = "Unknown Version"):

        # Store variables
        self.windowSize = (width, height)
        self.windowPosition = windowPosition
        self.windowBackgroundColor = background
        self.displayNumber = MCOv2.testDisplayNumber(displayNumber)
        self.cursor = self.cursorOptions[cursor]
        self.version = version

        # Move the window to its initial position
        self.moveWindow(self.windowPosition)

        # Create the window with settings
        self.screen = display.set_mode(size=self.windowSize, flags=self.displayTags if not fullscreen else self.displayTags | FULLSCREEN, display=self.displayNumber, depth=32, vsync=1)

        # Set the window title to that provided
        display.set_caption(version)

        # Configure the cursor type
        mouse.set_cursor(self.cursor)

    def start(self):
        """Runs the overlay"""

        self.running = True

        while self.running:

            # Check all events            
            for event in Event.get():
                self.checkEvent(event)

            # Draw the screen
            self.drawScreen()

    def stop(self):
        """Stops the overlay"""
        self.running = False
        display.quit()
        pygame.quit()
        exit()

    def checkEvent(self, event: Event):
        """Handles events

        Args:
            event (Event): Event to handle
        """
        # Retrieve the type
        type = event.type

        # Check events
        if type == QUIT:
            self.running = False
        elif type == KEYDOWN:
            if event.unicode == "q":
                self.running = False
            elif event.key == K_F11:
                self.toggleFullscreen()
            else:
                print("Key Down: {} - mod'{} / key'{} / scanc'{}".format(event.unicode, event.mod, event.key, event.scancode))
        elif type == KEYUP:
            print("Key Up: {} - mod'{} / key'{} / scanc'{}".format(event.unicode, event.mod, event.key, event.scancode))
        elif type == MOUSEMOTION:
            self.mouseButtons[0] = event.buttons[0] == 1
            self.mouseButtons[1] = event.buttons[1] == 1
            self.mouseButtons[2] = event.buttons[2] == 1
            self.mousePos = event.pos
            #print("Mouse moved to {}, relatively {} with buttons (L={}, R={}, M={})".format(event.pos, event.rel, self.mouseButtons[0], self.mouseButtons[2], self.mouseButtons[1]))
        elif type == MOUSEBUTTONDOWN or type == MOUSEBUTTONUP:
            if event.button > 10:
                print("WTF BUTTON INDEX > 10? HOLY SH!T: {}".format(event.button))
                return
            self.mouseButtons[event.button - 1] = type == MOUSEBUTTONDOWN
            button = "Unknown"
            if event.button == 1:
                button = "Left"
            elif event.button == 2:
                button = "Middle"
            elif event.button == 3:
                button = "Right"
            elif event.button == 4:
                button = "ScrollUp"
            elif event.button == 5:
                button = "ScrollDown"
            elif event.button == 6:
                button = "SideButton1"
            elif event.button == 7:
                button = "SideButton2"
            else:
                button += " ({})".format(event.button)
            print("{} mouse button {} at {}".format(button, "pressed" if type == MOUSEBUTTONDOWN else "released", event.pos))
            button = event.button
        elif type == DROPBEGIN:
            self.windowIsReceivingFile = True
            print("File incoming!")
        elif type == DROPCOMPLETE:
            self.windowIsReceivingFile = False
            print("File drop complete!")
        elif type == DROPFILE:
            print("File dropped's path is {}".format(event.file))
            self.newLogFile(event.file)
        elif type == WINDOWENTER:
            self.windowHasMouse = True
            print("Mouse entered window")
        elif type == WINDOWLEAVE:
            self.windowHasMouse = False
            print("Mouse left window")
        elif type == WINDOWFOCUSGAINED:
            self.windowIsFocused = True
            print("Focused window")
        elif type == WINDOWFOCUSLOST:
            self.windowIsFocused = False
            print("Unfocused window")
        elif type == WINDOWMOVED:
            print("Window moved from ({}, {}) to ({}, {})".format(self.windowPosition[0], self.windowPosition[1], event.x, event.y))
            self.windowPosition = (event.x, event.y)
        elif type == WINDOWMINIMIZED:
            print("Window minimised!")
            self.windowVisible = False
        elif type == WINDOWEXPOSED:
            print("Window made visible!")
            self.windowVisible = True
        elif type == WINDOWRESIZED:
            print(dir(event))
        #else:
            #print("Unhandled event: {}".format(type))

    def drawScreen(self):
        """Draws the full screen"""

        # Background color
        self.screen.fill(self.windowBackgroundColor)

        # Circle in the center for no reason
        draw.circle(self.screen, (0, 0, 255), (250, 250), 75)

        # Mouse muppet
        draw.rect(self.screen, Color(10, 100, 200, 50), Rect(self.mousePos[0] - 8, self.mousePos[1] - 8, 16, 16))

        # Flip (i.e. update) the display
        display.flip()

    def testDisplayNumber(displayNumber: int):
        """Tests if a display number is valid"""
        displays = display.get_num_displays()
        if displayNumber > displays:
            print("Selected window does not exist. Selected window {} of {} windows. Selecting highest number: {}".format(displayNumber, displays, displays))
            return displays
        elif displayNumber < 0:
            print("Selected window negative. Max window number is {}, selecting that one.".format(displays))
            return displays
        else:
            print("Selected window {}".format(displayNumber))
            return displayNumber

    def moveWindow(self, pos: tuple):
        os.environ["SDL_VIDEO_WINDOW_POS"] = "{}, {}".format(pos[0], pos[1])

    def toggleFullscreen(self):
        # This can be swapped out with a nicer looking window, that resizes the Surface to another width and height.
        # Code for that is:
        # -> fullscreen -> display.set_mode(display.list_modes()[0], FULLSCREEN)
        # -> windowed -> display.set_mode(self.windowSize)
        # Note that this requires scaling EVERYTHING suitably
        self.screen = display.set_mode(size=self.windowSize, flags=self.displayTags if not self.windowFullscreen else self.displayTags | FULLSCREEN, display=self.displayNumber, depth=32, vsync=1)
        self.windowFullscreen = not self.windowFullscreen

    def newLogFile(self, path: str):
        """Handles a new log file being dropped into the window"""
        if not path.endswith("\\logs\\latest.log"):
            print("Invalid file. Please try again")
        else:
            print("Valid log file, yeet!")
            self.logFile = path


if __name__ == "__main__":
    overlay = MCOv2(
        width=500, 
        height=500, 
        displayNumber=1,
        version="MCOv2 BETA 0.1",
    )
    overlay.start()