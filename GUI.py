from PySide6.QtWidgets import QApplication, QProgressBar, QPushButton, QTableView, QWidget, QHeaderView, QLabel
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt


class GUI:

    class Window:
        statistics = 1
        options = 2

    app = QApplication([])
    statisticsWindow = QWidget(f=Qt.FramelessWindowHint)
    optionsWindow = QWidget(f=Qt.FramelessWindowHint)
    defaultSizeX = 800
    defaultSizeY = 600
    newSizeX = None
    newSizeY = None
    hypixelAPILoad = 0
    minecraftAPILoad = 0
    overlayLoad = 0
    currentWindow = Window.statistics

    def __init__(self, winx: int, winy: int, version: str, statisticsTypes: list, statistics: dict):
        self.newSizeX = winx
        self.newSizeY = winy
        self.version = version
        self.stats = statistics
        self.statTypes = statisticsTypes
        self.buildStatistics()

    def buildWindow(self, window: QWidget):
        window.resize(self.newSizeX, self.newSizeY)
        font = QFont()
        font.setBold(False)
        font.setUnderline(False)
        font.setKerning(False)
        font.setWeight(QFont.Weight.Normal)
        window.setFont(font)
        window.setObjectName(u"background")
        window.setStyleSheet("QWidget#background {background-color: gray}")

    def buildOptions(self):
        self.buildWindow()
        QLabel("Options", self.optionsWindow)

    def buildStatistics(self):
        self.buildWindow(self.window())
        self.statTableMain = QTableView(self.window())
        self.statTableMain.setObjectName(u"statTableMain")
        statTableHeader = QHeaderView(Qt.Orientation.Vertical)
        # self.statTableMain.commitData()
        # https://doc.qt.io/qt-5/sql-model.html
        self.statTableMain.setVerticalHeader(statTableHeader)
        self.statTableMain.setGeometry(
            self.winw(5), self.winh(10),
            self.winw(90), self.winh(80)
        )
        hypixelAPILabel = QLabel("Hypixel API Load:", self.window())
        hypixelAPILabel.setGeometry(
            self.winw(5), self.winh(90),
            self.winw(15), self.winh(5)
        )
        minecraftAPILabel = QLabel("Minecraft API Load:", self.window())
        minecraftAPILabel.setGeometry(
            self.winw(20), self.winh(90),
            self.winw(15), self.winh(5)
        )
        overlayProgressLabel = QLabel("Overlay Load:", self.window())
        overlayProgressLabel.setGeometry(
            self.winw(35), self.winh(90),
            self.winw(15), self.winh(5)
        )
        self.hypixelProgressBar = QProgressBar(self.window())
        self.hypixelProgressBar.setValue(self.hypixelAPILoad)
        self.hypixelProgressBar.setGeometry(
            self.winw(5), self.winh(95),
            self.winw(15), self.winh(3)
        )
        self.minecraftProgressBar = QProgressBar(self.window())
        self.minecraftProgressBar.setValue(self.minecraftAPILoad)
        self.minecraftProgressBar.setGeometry(
            self.winw(20), self.winh(95),
            self.winw(15), self.winh(3)
        )
        self.overlayProgressBar = QProgressBar(self.window())
        self.overlayProgressBar.setValue(self.overlayLoad)
        self.overlayProgressBar.setGeometry(
            self.winw(35), self.winh(95),
            self.winw(15), self.winh(3)
        )
        self.statisticsButton = QPushButton("&Stats", self.window())
        self.statisticsButton.setGeometry(
            self.winw(5), self.winh(4),
            self.winw(10), self.winh(4)
        )
        self.statisticsButton.setObjectName(u"menuButton")
        self.optionsButton = QPushButton("&Options", self.window())
        self.optionsButton.setGeometry(
            self.winw(16), self.winh(4),
            self.winw(10), self.winh(4)
        )
        self.optionsButton.setObjectName(u"menuButton")
        self.exitButton = QPushButton("&Exit", self.window())
        self.exitButton.setGeometry(
            self.winw(85), self.winh(4),
            self.winw(10), self.winh(4)
        )
        self.exitButton.setObjectName(u"menuButton")

        self.statisticsButton.clicked.connect(
            lambda: self.statisticsButtonClick())
        self.optionsButton.clicked.connect(lambda: self.optionsButtonClick())
        self.exitButton.clicked.connect(lambda: self.exitButtonClick())

    def updateButtons(self):
        self.statisticsButton.setDisabled(
            self.currentWindow == self.Window.statistics)
        self.optionsButton.setDisabled(
            self.currentWindow == self.Window.options)

    def statisticsButtonClick(self):
        self.currentWindow = self.Window.statistics
        print("Switched to statistics window")

    def optionsButtonClick(self):
        self.currentWindow = self.Window.options
        print("Switched to options window")

    def exitButtonClick(self):
        self.app.exit()

    def winw(self, percent: int):
        return percent/100 * self.defaultSizeX

    def winh(self, percent: int):
        return percent/100 * self.defaultSizeY

    def scale(self, normal: int, dir="both"):
        size = self.window().size()
        xscale = size.width() / self.defaultSizeX
        yscale = size.height() / self.defaultSizeY
        normal *= xscale if dir == "both" or dir == "hor" else 1
        normal *= yscale if dir == "both" or dir == "ver" else 1
        return normal

    def window(self):
        if self.currentWindow == self.Window.statistics:
            return self.statisticsWindow
        else:
            return self.optionsWindow

    def run(self):
        self.window().show()
        self.app.exec_()


if __name__ == "__main__":
    gui = GUI(800, 600, "1.0", ["a", "b", "c"], {})
    gui.run()
