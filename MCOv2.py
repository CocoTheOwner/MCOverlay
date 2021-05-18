# Import and initialize the pygame library
from pygame import Color as rgba, color, time, freetype, Color, Rect, Surface, display, mouse, draw, cursors, event as Event
from pygame.freetype import Font
from pygame.constants import *
import pygame, random
pygame.init()

defaultWindowProperties = {
    "size": (400, 500),
    "minSize": (250, 300),
    "background": rgba(0,131,45,255), # Dark green
    "menuBar": {
        "x": 0,
        "y": 0,
        "w": "100",
        "h": 37.5,
        "background": rgba(234,67,53,255), # Dark red
    },
    "menuButtons": {
        "x": "5",
        "y": 7.5,
        "w": "90",
        "h": 22.5,
        "textColor": rgba(0,172,71,255),  # Light green
        "textFont": '',
        "background": rgba(0,131,45,255), # Dark green
        "padding": 1,
        "StatsX": 10,
        "OptionsX": 100,
        "FileX": 200,
        "ExitX": 300
    },
    "table": {
        "x": "5",
        "y": 52.5,
        "w": "90",
        "h": -120,
        "background": rgba(0,102,218,255), # Dark blue
        "text": rgba(0,102,218,255), # Light blue
        "headerLines": rgba(255,186,0,255), # Orang
        "headerText": rgba(0,131,45,255), # Dark green
        "separatorLines": rgba(255,186,0,128) # Orang with lower alpha
    },
    "progressBarContainter": {
        "x": "5",
        "y": -55,
        "w": "90",
        "h": 40,
        "background": rgba(0,102,218,255), # Dark blue
    },
    "progressBar": {
        "y": 17.5,
        "h": 20,
        "w": "27",
        "MCOProgressBarX": "2.25",
        "McAPIProgressBarX": "31.50",
        "hyAPIProgressBarX": "60.75",
        "outline": rgba(234,67,53,255), # Dark red
        "outlineSize": 1,
        "bar": rgba(0,131,45,255), # Dark green
        "noBar": rgba(0,102,218,255), # Dark blue
        "textColor": rgba(0,0,0,255), # Black
        "textSize": 10,
        "textFont": "Comic Sans MS",
        "headerTextY": 4,
        "headerTextH": 10,
        "headerTextColor": rgba(0,0,0,255), # Black
        "headerTextFont": "Comic Sans MS",
        "headerTextSize": 10
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
    windowOpen = None
    windows = ["Stats", "Options", "File", "Exit"]
    windowSize = None
    windowSizeMin = None
    windowProperties = None
    windowVisible = True
    windowPosition = None
    windowHasMouse = False
    windowIsFocused = False
    windowFullscreen = False
    windowIsReceivingFile = False
    windowButtons = []

    # Debug
    debugEvents = False
    debugButtons = False

    # Loads
    hyAPILoad = 0
    mcAPILoad = 0
    MCOLoad   = 0

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
        windowOpen = "Stats",
        fullscreen = False,
        displayNumber = 0,
        cursor = 0,
        version = "Unknown Version",
        debugEvents = False,
        debugButtons = False):

        # Store variables
        self.windowProperties = windowProperties
        self.windowPosition = windowPosition
        self.displayNumber = MCOv2.testDisplayNumber(displayNumber)
        self.windowFullscreen = fullscreen
        self.cursor = self.cursorOptions[cursor]
        self.version = version
        self.windowOpen = windowOpen
        self.windowSize = (width, height)
        self.debugEvents = debugEvents
        self.debugButtons = debugButtons
        self.enforceWindow()

        # Add menubutton
        self.createMenuButtons()
        x = freetype.SysFont("Comic Sans MS", 1)
        self.windowButtons.append(self.Button("Testbutton", Rect(10, 10, 50, 50), onClick=self.printMenuButtonBoop, color=Color(255, 255, 0), padding=2, font=x))

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

            time.wait(100)
            self.MCOLoad = (self.MCOLoad + random.randrange(0, 5)) % 100
            self.mcAPILoad = (self.mcAPILoad + random.randrange(0, 5)) % 100
            self.hyAPILoad = (self.hyAPILoad + random.randrange(0, 5)) % 100

            # Draw the screen
            self.drawScreen()

        # Stop if the loop is over
        self.stop()

    def stop(self):
        """Stops the overlay"""
        self.running = False
        display.quit()
        pygame.quit()
        exit()

    def setResetScreen(self):
        self.screen = display.set_mode(
            size=self.windowSize,
            flags=self.displayTags if not self.windowFullscreen else self.displayTags | FULLSCREEN,
            display=self.displayNumber,
            depth=32,
            vsync=1
        )

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
                if self.debugEvents: print("Key Down: {} - mod'{} / key'{} / scanc'{}".format(event.unicode, event.mod, event.key, event.scancode))
        elif type == KEYUP:
            if self.debugEvents: print("Key Up: {} - mod'{} / key'{} / scanc'{}".format(event.unicode, event.mod, event.key, event.scancode))
        elif type == MOUSEMOTION:
            self.mouseButtons[0] = event.buttons[0] == 1
            self.mouseButtons[1] = event.buttons[1] == 1
            self.mouseButtons[2] = event.buttons[2] == 1
            self.mousePos = event.pos
            #if self.debugEvents: print("Mouse moved to {}, relatively {} with buttons (L={}, R={}, M={})".format(event.pos, event.rel, self.mouseButtons[0], self.mouseButtons[2], self.mouseButtons[1]))
        elif type == MOUSEBUTTONDOWN or type == MOUSEBUTTONUP:
            if event.button > 10:
                if self.debugEvents: print("WTF BUTTON INDEX > 10? HOLY SH!T: {}".format(event.button))
                return
            self.mouseButtons[event.button - 1] = type == MOUSEBUTTONDOWN
            button = "Unknown"
            if event.button == 1:
                button = "Left"
                if type == MOUSEBUTTONDOWN:
                    self.leftClicked(event.pos)
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
            if self.debugEvents: print("{} mouse button {} at {}".format(button, "pressed" if type == MOUSEBUTTONDOWN else "released", event.pos))
            button = event.button
        elif type == DROPBEGIN:
            self.windowIsReceivingFile = True
            if self.debugEvents: print("File incoming!")
        elif type == DROPCOMPLETE:
            self.windowIsReceivingFile = False
            if self.debugEvents: print("File drop complete!")
        elif type == DROPFILE:
            if self.debugEvents: print("File dropped's path is {}".format(event.file))
            self.newLogFile(event.file)
        elif type == WINDOWENTER:
            self.windowHasMouse = True
            if self.debugEvents: print("Mouse entered window")
        elif type == WINDOWLEAVE:
            self.windowHasMouse = False
            if self.debugEvents: print("Mouse left window")
        elif type == WINDOWFOCUSGAINED:
            self.windowIsFocused = True
            if self.debugEvents: print("Focused window")
        elif type == WINDOWFOCUSLOST:
            self.windowIsFocused = False
            if self.debugEvents: print("Unfocused window")
        elif type == WINDOWMOVED:
            if self.debugEvents: print("Window moved from ({}, {}) to ({}, {})".format(self.windowPosition[0], self.windowPosition[1], event.x, event.y))
            self.windowPosition = (event.x, event.y)
        elif type == WINDOWMINIMIZED:
            if self.debugEvents: print("Window minimised!")
            self.windowVisible = False
        elif type == WINDOWEXPOSED:
            if self.debugEvents: print("Window made visible!")
            self.windowVisible = True
        elif type == WINDOWRESIZED:
            x = (event.x, event.y)
            if self.debugEvents: print("Window resized from {} to {}".format(self.windowSize, x))
            self.windowSize = x
            self.enforceWindow()
        #elif self.debugEvents: print("Unhandled event: {}".format(type))

    def leftClicked(self, pos: tuple):
        for button in self.windowButtons:
            button.checkIfClicked(pos, True)

    def drawScreen(self):
        """Draws the full screen"""

        # Background color
        self.screen.fill(self.windowProperties["background"])

        # Draw menu bar
        self.makeMenu()

        if self.windowOpen == self.windows[0]: # Stats window

            # Draw table
            self.makeTable()

            # Draw API load
            self.makeProgressBars()

        elif self.windowOpen == self.windows[1]: # Options window

            draw.line(self.screen, Color(12, 153, 10), (0,0), (100,100))
            
        elif self.windowOpen == self.windows[2]: # File window

            draw.line(self.screen, Color(0, 0, 255), (0,0), (100,100))

        elif self.windowOpen == self.windows[3]: # Exit button pressed

            self.running = False

        # Flip (i.e. update) the display
        display.flip()

    def makeMenu(self):

        # Make the surface
        menuBar = Surface(size=(
            self.getWindowProperty("menuBar", "w"),
            self.getWindowProperty("menuBar", "h")
        ))

        # Color the background
        menuBar.fill(self.getWindowProperty("menuBar", "background", isPosition=False))

        # Add menu buttons
        for button in self.windowButtons:
            if self.debugButtons: print("Bitt1")
            button.drawSelf(menuBar)

        # Blit the menu bar onto the main screen
        self.screen.blit(menuBar, (
            self.getWindowProperty("menuBar", "x"),
            self.getWindowProperty("menuBar", "y")
        ))

    def printMenuButtonBoop():
        print("Boop!")

    def makeTable(self):
        draw.rect(
            self.screen, 
            self.getWindowProperty("table", "background", isPosition=False), 
            Rect(
                self.getWindowProperty("table", "x"), 
                self.getWindowProperty("table", "y"), 
                self.getWindowProperty("table", "w"),
                self.getWindowProperty("table", "h")
            )
        )

    def makeProgressBars(self):

        # Create a progressbar
        progressBars = Surface(size=(
            self.getWindowProperty("progressBarContainter", "w"),
            self.getWindowProperty("progressBarContainter", "h")
        ))
        
        # Fill the progressbar with the proper background color
        progressBars.fill(self.getWindowProperty("progressBarContainter", "background", isPosition=False))
        
        # Blit progressbars onto main progressbar
        progressBars.blit(self.createLoadBar(self.MCOLoad), dest=(
            self.getWindowProperty("progressBar", "MCOProgressBarX"),
            self.getWindowProperty("progressBar", "y")
        ))
        progressBars.blit(self.createLoadBar(self.mcAPILoad), dest=(
            self.getWindowProperty("progressBar", "McAPIProgressBarX"),
            self.getWindowProperty("progressBar", "y")
        ))
        progressBars.blit(self.createLoadBar(self.hyAPILoad), dest=(
            self.getWindowProperty("progressBar", "hyAPIProgressBarX"),
            self.getWindowProperty("progressBar", "y")
        ))
        progressBars.blit(self.createLoadBarHeader("Overlay Load"), dest=(
            self.getWindowProperty("progressBar", "MCOProgressBarX"),
            self.getWindowProperty("progressBar", "headerTextY")
        ))
        progressBars.blit(self.createLoadBarHeader("MCAPI Load"), dest=(
            self.getWindowProperty("progressBar", "McAPIProgressBarX"),
            self.getWindowProperty("progressBar", "headerTextY")
        ))
        progressBars.blit(self.createLoadBarHeader("HYAPI Load"), dest=(
            self.getWindowProperty("progressBar", "hyAPIProgressBarX"),
            self.getWindowProperty("progressBar", "headerTextY")
        ))

        # Draw the progressbar with contents to the screen
        self.screen.blit(progressBars, dest=(
            self.getWindowProperty("progressBarContainter", "x"),
            self.getWindowProperty("progressBarContainter", "y")
        ))

    def createLoadBarHeader(self, title: str):
        headerWidth: float = self.getWindowProperty("progressBar", "w")
        headerFont: Font = freetype.SysFont(
            self.getWindowProperty("progressBar", "headerTextFont", isPosition=False),
            1
        )
        headerSize = self.getWindowProperty("progressBar", "headerTextSize", isPosition=False)
        headerColor = self.getWindowProperty("progressBar", "headerTextColor", isPosition=False)
        headerHeight = self.getWindowProperty("progressBar", "headerTextH", isPosition=False)

        text, area = headerFont.render(title, fgcolor=headerColor, size=headerSize)
        header = Surface((headerWidth, headerHeight))
        header.fill(self.getWindowProperty("progressBarContainter", "background", isPosition=False))
        header.blit(text, (headerWidth/2-area.width/2, headerHeight/2-area.height/2))
        return header

    def createLoadBar(self, load: int):

        # Retrieve progressBar properties
        width: float = self.getWindowProperty("progressBar", "w")
        height: float = self.getWindowProperty("progressBar", "h")
        outlineSize: float = self.getWindowProperty("progressBar", "outlineSize")
        font: Font = freetype.SysFont(
            self.getWindowProperty("progressBar", "textFont", isPosition=False),
            1
        )
        textSize = self.getWindowProperty("progressBar", "textSize", isPosition=False)
        textColor = self.getWindowProperty("progressBar", "textColor", isPosition=False)

        # Create the bar
        bar = Surface((width, height))

        # Draw the background with the outline color
        bar.fill(self.getWindowProperty("progressBar", "outline", isPosition=False))
        
        # Draw the center of the bar with the noBar color
        draw.rect(bar, self.getWindowProperty("progressBar", "noBar", isPosition=False),
            Rect(
                outlineSize, outlineSize, 
                width - outlineSize * 2,
                height - outlineSize * 2
            )
        )

        # Fill the bar with the proper width bar indicative of the load
        draw.rect(bar, self.getWindowProperty("progressBar", "bar", isPosition=False),
            Rect(
                outlineSize*2, outlineSize*2,
                width * load/100 - outlineSize*4, height-outlineSize*4
            )
        )

        # Calculate position of text center
        if load > 100:
            x = 0.5
        elif load > 100-load:
            x = load/100/2
        else:
            x = load/100+(100-load)/200
        x = width * x

        # Draw the load onto the bar
        text, area = font.render(str(load) + "%", fgcolor=textColor, size=textSize)
        bar.blit(text, (x-area.width/2, height/2-area.height/2))

        return bar

    def createMenuButtons(self):
        return Surface((50, 50))

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

    def enforceWindow(self):
        minSize = self.getWindowProperty("minSize", isPosition=False)
        x = max(self.windowSize[0], minSize[0])
        y = max(self.windowSize[1], minSize[1])
        self.windowSize = (x, y)
        self.setResetScreen()

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
        return position / self.getWindowProperty("size", isPosition=False)[0] * self.windowSize[0]

    def yPos(self, position: int):
        """Translates position based on default window size"""
        if position < 0:
            position = self.windowSize[0] + position
        return position / self.getWindowProperty("size", isPosition=False)[1] * self.windowSize[1]

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

    class Button:
        name: str = None # This is also the text that appears on it
        color: Color = None
        dimensions: Rect = None
        onClick = None
        isActive: bool = None
        isEnabled: bool = None
        padding: int = None
        font: Font = None
        
        def __init__(self, uniqueName: str, dimensions: Rect, onClick, color: Color, padding: int, font: Font, isEnabled = True, isActive = False, textSize = 20, textColor = Color(0,0,0,0)):
            self.name = uniqueName
            self.dimensions = dimensions
            self.onClick = onClick
            self.color = color
            self.padding = padding
            self.isEnabled = isEnabled
            self.isActive = isActive
            self.font = font
            self.textSize = textSize
            self.textColor = textColor
            """
            freetype.SysFont(
            self.getWindowProperty("progressBar", "textFont", isPosition=False),
            1
            )
            """

        def checkIfClicked(self, position: tuple, debug = False):
            if debug:
                print("Checking button: " + self.name)
            if position[0] > self.dimensions.x and position[0] < self.dimensions.x + self.dimensions.w\
                and position[1] > self.dimensions.y and position[1] < self.dimensions.y + self.dimensions.h:
                print("Clicked button: " + self.name)
                print(self.onClick.__name__)
                return True
            return False

        def drawSelf(self, surface: Surface):
            color = self.color if not self.isActive else Color(self.color.lerp(Color(0,0,0,0), 0.15))
            draw.rect(surface, Color(255, 255, 255, 255), Rect(
                self.dimensions.x - self.padding, self.dimensions.y + self.padding,
                self.dimensions.w-2*self.padding, self.dimensions.h+2*self.padding,
            ))
            draw.rect(surface, color, Rect(
                self.dimensions.x - self.padding, self.dimensions.y + self.padding,
                self.dimensions.w-2*self.padding, self.dimensions.h+2*self.padding,
            ))
            

if __name__ == "__main__":
    overlay = MCOv2(
        version="MCOv2 BETA 0.1",
        displayNumber=1
    )
    overlay.start()