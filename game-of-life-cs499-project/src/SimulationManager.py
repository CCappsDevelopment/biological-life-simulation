'''
# ----------------------------------------------------------------
#
# SimulationManager.py
#
# Handles Simulation Thread functionality.
# Houses the main Simulation event loop.
# Handles setting up the initial state of the Simulation.
# Handles input from the GUI.
#
# Implemented as a Singleton Class.
# ----------------------------------------------------------------
'''

from PyQt5.QtCore import QThread, pyqtSignal, QObject
from DataParser import DataParser
from WorldData import WorldData as wd
import GameOfLife as gui
from Report import Report


class SimulationManager(QThread):

    __instance = None
    drawSignal = pyqtSignal(list, list, list, list)

    def __init__(self):
        QThread.__init__(self)
        self.simTime = 0
        self.simSpeed = 1000
        self.worldData = wd.getInstance()
        # if SimulationManager.__instance:
        # print("Instance already created.\n", SimulationManager.__instance)

    @classmethod
    def getInstance(sm):
        if not sm.__instance:
            sm.__instance = SimulationManager()
            # print("Creating Instance...\n", SimulationManager.__instance)
        return sm.__instance

    # Destructor - Halts thread
    def __del__(self):
        self.wait()

    # Called when the Thread is created
    def run(self):
        self.Update()

    # Initialize Simulation World
    def InitSimulation(self):
        if self.simTime == 0.0:
            self.worldData.InitWorldData()
            # print("Initializing Simulation...")

    # Update all components of the simulation
    # may call update functions for other classes
    def Update(self):
        self.simTime += 1
        self.worldData.Update()

        self.drawSignal.emit(self.worldData.plants,
                             self.worldData.grazers,
                             self.worldData.predators,
                             self.worldData.obstacles)

    # Starts Sim Thread

    def StartSimThread(self):
        self.start()
        # print("Starting Simulation...")

    def PrintReport(self):
        data = list(self.worldData.plants)
        data.extend(list(self.worldData.grazers))
        data.extend(list(self.worldData.predators))
        data.extend(list(self.worldData.obstacles))
        report = Report()
        report.create(data, self.simTime)

    # Kills Sim Thread
    def KillSimThread(self):
        self.terminate()
        self.__del__()
        self.simTime = 0.0
        self.worldData.ResetWorld()
