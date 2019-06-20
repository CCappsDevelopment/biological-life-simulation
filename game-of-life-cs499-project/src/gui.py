'''
# gui.py - Handles starting the Graphical User Interface for the Simulation

'''

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette
from PyQt5.QtCore import Qt
from GameOfLife import GameOfLife
from DataParser import DataParser

APP = QApplication(sys.argv)
APP.setStyleSheet(open('styles.css').read())

PARSER = DataParser()
PARSER.LoadDataFile("inputData.xml")

WINDOW = GameOfLife()
sys.exit(APP.exec_())
