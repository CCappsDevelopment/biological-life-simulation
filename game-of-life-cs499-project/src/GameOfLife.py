from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QLabel, QComboBox
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPainter, QPen, QBrush, QColor
from PyQt5.QtCore import pyqtSlot, QTimer, pyqtSignal
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QMainWindow
from WorldData import WorldData as wd
import SimulationManager as sm
from Predator import PredatorLifeStages
from Plant import PlantLifeStages


class GridLabel(QLabel):

    def __init__(self, parent=None):
        super(GridLabel, self).__init__(parent=parent)
        self.rect = parent.rect
        self.guiIcons = []

    def setGuiIcons(self, guiIcons):
        self.guiIcons = guiIcons

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        if(len(self.guiIcons) > 0):
            for icon in self.guiIcons:
                icon.drawIcon(painter)


class GuiIcon(object):
    def __init__(self, icon, x, y, diameter=0, pen=QPen(Qt.green, 4, Qt.SolidLine)):
        self.Icon = icon.scaled(diameter, diameter)
        self.X = x - (diameter / 2)
        self.Y = y - (diameter / 2)
        self.Diameter = diameter
        self.Pen = pen

    def drawIcon(self, painter):
        painter.drawPixmap(self.X, self.Y, self.Icon)


class GameOfLife(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'the game of life.'
        self.left = 100
        self.top = 100
        self.width = 1200
        self.height = 770
        self.initUI()

        self.simThread = sm.SimulationManager.getInstance()
        self.simTimer = QTimer()
        self.simTimer.timeout.connect(self.simThread.Update)
        self.simThread.drawSignal.connect(self.DrawSimulation)

        self.worldData = wd.getInstance()

    def initUI(self):

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width, self.height)

        # play button
        self.playButton = QPushButton(QIcon('play.png'), '', self)
        self.playButton.resize(50, 50)
        self.playButton.move(1020, 650)
        self.playButton.setShortcut('Ctrl+S')
        self.playButton.setStatusTip('Start the simulation')
        self.playButton.clicked.connect(self.on_play_clicked)

        # pause button
        self.pauseButton = QPushButton(QIcon('pause.png'), '', self)
        self.pauseButton.resize(50, 50)
        self.pauseButton.move(1080, 650)
        self.pauseButton.setShortcut('Ctrl+P')
        self.pauseButton.setStatusTip('Pause the simulation')
        self.pauseButton.clicked.connect(self.on_pause_clicked)

        # stop button
        self.stopButton = QPushButton(QIcon('stop.png'), '', self)
        self.stopButton.resize(50, 50)
        self.stopButton.move(1140, 650)
        self.stopButton.setShortcut('Ctrl+X')
        self.stopButton.setStatusTip('Stop the simulation')
        self.stopButton.clicked.connect(self.on_stop_clicked)

        # report button
        self.reportButton = QPushButton(QIcon('report.png'), '', self)
        self.reportButton.resize(50, 50)
        self.reportButton.move(1140, 710)
        self.reportButton.setShortcut('Ctrl+R')
        self.reportButton.setStatusTip('Generate a realtime report')
        self.reportButton.clicked.connect(self.on_report_clicked)

        # simulation speed mltiplier box
        self.multiplierBox = QComboBox(self)
        self.multiplierBox.addItems(['1X', '10X', '50X', '100X'])
        self.multiplierBox.currentIndexChanged.connect(
            self.on_multiplier_change)
        self.multiplierBox.resize(110, 50)
        self.multiplierBox.move(1020, 710)

        self.playButton.setStyleSheet('background-color:#004080')
        self.pauseButton.setStyleSheet('background-color:#004080')
        self.stopButton.setStyleSheet('background-color:#004080')
        self.reportButton.setStyleSheet('background-color:#004080')
        self.multiplierBox.setStyleSheet(
            'background-color:#004080;color: white')

        # grid area (sketch)
        self.grid = QPixmap('grid.png')
        # grid container
        self.gridContainer = GridLabel(self)
        self.gridContainer.setPixmap(self.grid)
        self.gridContainer.resize(1000, 750)
        self.gridContainer.move(10, 10)

        # sidebar
        self.sidebar = QPixmap('sidebar.png')

        # sidebar container
        self.sidebarContainer = QLabel('', self)
        self.sidebarContainer.setPixmap(self.sidebar)
        self.sidebarContainer.resize(170, 630)
        self.sidebarContainer.move(1020, 10)

        self.show()

    @pyqtSlot()
    def on_play_clicked(self):
        # print("play clicked")
        self.simThread.InitSimulation()
        self.simThread.StartSimThread()
        self.SetSimSpeed()
        self.simTimer.start(self.simThread.simSpeed)
        return

    @pyqtSlot()
    def on_pause_clicked(self):
        # print("pause clicked")
        self.simTimer.stop()
        return

    @pyqtSlot()
    def on_stop_clicked(self):
        # print("stop clicked")
        self.simThread.KillSimThread()
        self.simTimer.stop()
        self.gridContainer.setGuiIcons([])
        self.repaint()
        return

    @pyqtSlot()
    def on_report_clicked(self):
        # print("report clicked")
        self.simThread.PrintReport()
        return

    @pyqtSlot()
    def on_multiplier_change(self):
        # print("speed set to " + self.multiplierBox.currentText())
        self.SetSimSpeed()
        if self.simTimer.isActive():
            self.simTimer.start(self.simThread.simSpeed)
        return

    def SetSimSpeed(self):
        if self.multiplierBox.currentText() == "1X":
            # TODO: Set Timer to execute every 1 Second.
            self.simThread.simSpeed = 1000
        elif self.multiplierBox.currentText() == "10X":
            # TODO: Set Timer to execute every 0.1 Seconds.
            self.simThread.simSpeed = 100
        elif self.multiplierBox.currentText() == "50X":
            # TODO: Set Timer to execute every 0.02 Seconds.
            self.simThread.simSpeed = 20
        elif self.multiplierBox.currentText() == "100X":
            # TODO: Set Timer to execute every 0.01 Seconds.
            self.simThread.simSpeed = 10

    # Draws current state of simulation to GUI
    # called every 1 second real time
    @pyqtSlot(list, list, list, list)
    def DrawSimulation(self, plants, grazers, predators, obstacles):
        # print("\n[---------------------------- D R A W I N G  S I M U L A T I O N ----------------------------]\n\n")

        guiIcons = []
        plantIcon = QPixmap('icons/adultplant.png')
        seedIcon = QPixmap('icons/seed.png')
        seedlingIcon = QPixmap('icons/seedling.png')
        seedingPlantIcon = QPixmap('icons/adultplantSeeding.png')
        grazerIcon = QPixmap('icons/adultCrab.png')
        predatorIcon = QPixmap('icons/teenShrimp.png')
        matingPredatorIcon = QPixmap('icons/reproductiveAdultShrimp.png')
        obstacleIcon = QPixmap('icons/rock.png')

        for plant in plants:
            if(plant["plant"].LifeStage == PlantLifeStages.Adult):
                guiIcons.append(GuiIcon(plantIcon, plant["plant"].X, plant["plant"].Y, plant["plant"].Diameter, QPen(
                    Qt.darkGreen, 4, Qt.SolidLine)))
            elif(plant["plant"].LifeStage == PlantLifeStages.SeedingAdult):
                guiIcons.append(GuiIcon(seedingPlantIcon, plant["plant"].X, plant["plant"].Y, plant["plant"].Diameter, QPen(
                    Qt.darkGreen, 4, Qt.SolidLine)))
            elif(plant["plant"].LifeStage == PlantLifeStages.Seed):
                guiIcons.append(GuiIcon(seedIcon, plant["plant"].X, plant["plant"].Y, plant["plant"].Diameter, QPen(
                    Qt.darkGreen, 4, Qt.SolidLine)))
            elif(plant["plant"].LifeStage == PlantLifeStages.Seedling):
                guiIcons.append(GuiIcon(seedlingIcon, plant["plant"].X, plant["plant"].Y, plant["plant"].Diameter, QPen(
                    Qt.darkGreen, 4, Qt.SolidLine)))

        for grazer in grazers:
            guiIcons.append(GuiIcon(grazerIcon, grazer["grazer"].X, grazer["grazer"].Y, 25, QPen(
                Qt.yellow, 1, Qt.SolidLine)))

        for predator in predators:
            if(predator["predator"].LifeStage == PredatorLifeStages.MatingAdult):
                guiIcons.append(GuiIcon(
                    matingPredatorIcon, predator["predator"].X, predator["predator"].Y, 25, QPen(Qt.red, 1, Qt.SolidLine)))
            else:
                guiIcons.append(GuiIcon(
                    predatorIcon, predator["predator"].X, predator["predator"].Y, 25, QPen(Qt.red, 1, Qt.SolidLine)))

        for obstacle in obstacles:
            guiIcons.append(GuiIcon(obstacleIcon, obstacle['obstacle'].X, obstacle['obstacle'].Y, obstacle['obstacle'].Diameter, QPen(
                Qt.gray, 1, Qt.SolidLine)))

        self.gridContainer.setGuiIcons(guiIcons)

        self.repaint()

        # print("Drawing Simulation...")

    # def paintEvent(self, event):
