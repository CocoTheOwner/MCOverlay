# Import and initialize the pygame library
import pygame, os
from pygame import Color as rgba, Color, Rect, Surface, display, mouse, draw, cursors, event as Event
from pygame.constants import *
pygame.init()

defaultWindowProperties = {
    "size": (400, 500),
    "minSize": (10, 20),
    "background": rgba(0,131,45,255), # Dark green
    "menu": {
        "x": 0,
        "y": 0,
        "w": "100",
        "h": 37.5,
        "background": rgba(234,67,53,255), # Dark red
        "text": rgba(0,172,71,255)  # Light green
    },
    "table": {
        "x": "5",
        "y": 56.25,
        "w": "90",
        "background": rgba(0,102,218,255), # Dark blue
        "text": rgba(0,102,218,255), # Light blue
        "headerLines": rgba(255,186,0,255), # Orang
        "headerText": rgba(0,131,45,255), # Dark green
        "separatorLines": rgba(255,186,0,128) # Orang with lower alpha
    },
    "progressBar": {
        "x": "5",
        "y": -35,
        "w": "90",
        "h": 25,
        "outline": rgba(234,67,53,255), # Dark red
        "bar": rgba(0,131,45,255), # Dark green
        "barFlash": rgba(0,172,71,255), # Light green
        "background": rgba(0,102,218,255), # Dark blue
        "text": rgba(0,102,218,255) # Light blue
    },
    "filePopup": {
        "background": rgba(0,172,71,255), # Light green
        "text": rgba(38,132,252,255), # Light blue
        "headerText": rgba(255,186,0,255) # Orang
    }
}
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
    displayTags = SRCALPHA | SHOWN | RESIZABLE

    # Window
    screen = None
    running = False
    windowSize = None
    windowSizeMin = None
    windowProperties = None
    windowVisible = True
    windowPosition = None
    windowHasMouse = False
    windowIsFocused = False
    windowFullscreen = False
    windowIsReceivingFile = False

    # Buttons
    mouseButtons = [False for _ in range(0,10)]
    mousePos = (0, 0)

    # Logfile
    logFile = None

    def __init__(
        self,
        width = 500,
        height = 500,
        windowPosition = defaultWindowProperties["size"],
        windowProperties = defaultWindowProperties,
        fullscreen = False,
        displayNumber = 0,
        cursor = 0,
        version = "Unknown Version"):

        # Store variables
        self.windowProperties = windowProperties
        self.windowSize = (width, height)
        self.windowPosition = windowPosition
        self.displayNumber = MCOv2.testDisplayNumber(displayNumber)
        self.cursor = self.cursorOptions[cursor]
        self.version = version

        # Create the window with settings
        self.screen = display.set_mode(
            size=self.windowSize,
            flags=self.displayTags if not fullscreen else self.displayTags | FULLSCREEN,
            display=self.displayNumber,
            depth=32,
            vsync=1
        )

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
            x = (event.x, event.y)
            print("Window resized from {} to {}".format(self.windowSize, x))
            self.handleResize(x)
            self.windowSize = x
        #else:
            #print("Unhandled event: {}".format(type))

    def drawScreen(self):
        """Draws the full screen"""

        # Background color
        self.screen.fill(self.windowProperties["background"])

        # Draw menu bar
        self.makeMenu()

        # Draw table
        self.makeTable()

        # Draw API load
        self.makeProgressBars()

        # Flip (i.e. update) the display
        display.flip()

    def makeMenu(self):
        draw.rect(
            self.screen, 
            self.getWindowProperty("menu", "background", False), 
            Rect(
                self.getWindowProperty("menu", "x"), 
                self.getWindowProperty("menu", "y"), 
                self.getWindowProperty("menu", "w"),
                self.getWindowProperty("menu", "h")
            )
        )

    def makeTable(self):
        draw.rect(
            self.screen, 
            self.getWindowProperty("table", "background", False), 
            Rect(
                self.getWindowProperty("table", "x"), 
                self.getWindowProperty("table", "y"), 
                self.getWindowProperty("table", "w"),
                self.windowSize[1] - 
                self.getWindowProperty("menu", "h") - 
                abs(self.getWindowProperty("progressBar", "y"))
            )
        )

    def makeProgressBars(self):
        draw.rect(
            self.screen, 
            self.getWindowProperty("progressBar", "background", False), 
            Rect(
                self.getWindowProperty("progressBar", "x"),
                self.getWindowProperty("progressBar", "y"),
                self.getWindowProperty("progressBar", "w"),
                self.getWindowProperty("progressBar", "h"),
            )
        )

    def getWindowProperty(self, element, subelement=None, isPosition=True, axis="x"):
        elements = {
            "x": "x",
            "X": "x",
            "y": "y",
            "Y": "y",
            "w": "x",
            "W": "x",
            "h": "y",
            "H": "y"
        }
        if subelement == None:
            if element in elements:
                axis = elements[element]
            if isPosition:
                return self.makePosition(self.windowProperties[element], axis)
            else:
                return self.windowProperties[element]
        else:
            if subelement in elements:
                axis = elements[subelement]
            if isPosition:
                return self.makePosition(self.windowProperties[element][subelement], axis)
            else:
                return self.windowProperties[element][subelement]

    def makePosition(self, position, axis):
        if axis != "x" and axis != "y":
            raise ValueError("Invalid axis provided (must be x, X, y, Y): {}".format(axis))
        if type(position) is float or type(position) is int:
            if position < 0:
                if axis == "x":
                    position = self.windowSize[0] + position
                else:
                    position = self.windowSize[1] + position
            return position
        elif type(position) is str:
            if position == "-7.5":
                print(axis)
            if axis == "x":
                return self.xPerc(float(position))
            else:
                return self.yPerc(float(position))
        else:
            raise ValueError("Position ({}) is not string or float but: {}".format(position, type(position)))

    def handleResize(self, newSize: tuple):
        if newSize[0] < self.getWindowProperty("minSize", False)[0]:
             or\
            newSize[1] < self.getWindowProperty("minSize", False)[1]:
            self.resizeWindow()

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

    def xPos(self, position: int):
        """Translates position based on default window size"""
        if position < 0:
            position = self.windowSize[0] + position
        return position / self.getWindowProperty("size", False)[0] * self.windowSize[0]

    def yPos(self, position: int):
        """Translates position based on default window size"""
        if position < 0:
            position = self.windowSize[0] + position
        return position / self.getWindowProperty("size", False)[1] * self.windowSize[1]

    def xPerc(self, percent: int):
        if percent < -100 or percent > 100:
            raise ValueError("Percentages range from -100 to 100")
        """Translates position based on default window size"""
        if percent < 0:
            return (100+percent)/100 * self.windowSize[0]
        else:
            return percent/100 * self.windowSize[0]

    def yPerc(self, percent: int):
        if percent < -100 or percent > 100:
            raise ValueError("Percentages range from -100 to 100")
        """Translates position based on default window size"""
        if percent < 0:
            return (100+percent)/100 * self.windowSize[1]
        else:
            return percent/100 * self.windowSize[1]
            
        

if __name__ == "__main__":
    overlay = MCOv2(
        version="MCOv2 BETA 0.1",
        displayNumber=1
    )
    overlay.start()