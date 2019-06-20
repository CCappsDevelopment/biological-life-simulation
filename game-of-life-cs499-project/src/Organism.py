from abc import ABC, abstractmethod


class Organism(ABC):

    def __init__(self, X, Y):
        self.X = X
        self.Y = Y
        super().__init__()

    @abstractmethod
    def PerformNextAction(self):
        pass


class Grazer(Organism):
    def __init__(self, X, Y, energyLevel):
        self.EnergyLevel = energyLevel
        super().__init__(X, Y)

    def PerformNextAction(self):
        self.X = self.X + 1


class Obstacle(Organism):
    def __init__(self, X, Y, diameter, height):
        self.Diameter = diameter
        self.Height = height
        super().__init__(X, Y)

    def PerformNextAction(self):
        self.X = self.X + 1
