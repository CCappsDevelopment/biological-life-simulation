# Import needed libraries
from pydispatch import dispatcher
import DataParser
import EventSignals
from enum import Enum
from random import random
import random
import math


class PlantLifeStages(Enum):
    Seed = 0
    Seedling = 1
    Adult = 2
    SeedingAdult = 3


# Defining our Class
class Plant():

    def __init__(self, X, Y, diameter, lifestage=PlantLifeStages.Seed):
        # Initialize xposition
        self.X = X
        # Initialize yposition
        self.Y = Y
        # Initialize diameter
        self.Diameter = diameter
        # Initialize Lifestage
        self.LifeStage = lifestage
        # Initialize Seeding
        self.Seeding = False
        # Initialize Living
        self.Alive = True

        self.dataParser = DataParser.DataParser.getInstance()

        # Timing vars
        # Time since the seed was first dropped
        self.timeSinceSeed = 0

        # Time since the last seed was dropped
        self.timeSinceLastSeedDroped = 3600

        # Keep track of the ammount of seeds dropped
        self.totalSeedsDropped = 0

    def SetId(self, idStr):
        self.Id = idStr

    def SetDiameter(self, diameter):
        if diameter > self.dataParser.MaxPlantSize:
            diameter = self.dataParser.MaxPlantSize
        # set the diameter
        self.Diameter = diameter

    def SetLocation(self, x, y):
        # Set the x position
        self.X = x
        # Set the y position
        self.Y = y

    def SetLifeStage(self, lifeStage):
        # Life stage can be 'Seed',
        # 'Seedling', 'Adult', & 'SeedingAdult' from enum PlantLifeStages
        self.LifeStage = lifeStage

    def Death(self):
        # The Plant has been eaten or has died
        self.Alive = False
        dispatcher.send(signal=EventSignals.plantDeath, sender=self.Id)

    def GetLocation(self):
        # Return the x and y position
        return self.X, self.Y

    def GetDiameter(self):
        # Return the diameter
        return self.Diameter

    def ReadyToSeed(self):
        if self.Alive and self.LifeStage == PlantLifeStages.SeedingAdult:
            self.Seeding = True

    def ReleaseSeed(self):
        location = self.CastSeedLocation()
        if (location[0] <= 900 and location[0] >= 100) and (location[1] <= 650 and location[1] >= 100):
            seed = Plant(location[0], location[1], 0.1)
            dispatcher.send(signal=EventSignals.plantCreation, sender=self.Id, newPlant=seed)
            self.totalSeedsDropped += 1

    def GetLifeStage(self):
        # Return the life stage
        return self.LifeStage

    def UpdateLifeStage(self):
        # Updating LiveStage
        if self.Diameter == self.dataParser.MaxPlantSize:
            self.LifeStage = PlantLifeStages.SeedingAdult
            self.ReadyToSeed()
        elif self.Diameter >= 25:
            self.LifeStage = PlantLifeStages.Adult
        elif self.Diameter > 0.1:
            self.LifeStage = PlantLifeStages.Seedling
        else:
            self.LifeStage = PlantLifeStages.Seed

    def PerformNextAction(self):

        # Update LifeStage before we move on
        self.UpdateLifeStage()

        # Doing actions based on life stage
        if self.LifeStage == PlantLifeStages.Seed:
            if self.timeSinceSeed < 10:
                self.timeSinceSeed += 1
            else:
                # If the seed sprouts it starts growing
                if random.random() > self.dataParser.SeedViabilityPercentage:
                    self.SetDiameter(self.Diameter + self.dataParser.PlantGrowthRate)
                else:  # Otherwise it dies
                    self.Death()
        elif self.LifeStage == PlantLifeStages.Seedling or self.LifeStage == PlantLifeStages.Adult:
            self.SetDiameter(self.Diameter + self.dataParser.PlantGrowthRate)  # plants just grow until they reach max size
        elif self.LifeStage == PlantLifeStages.SeedingAdult:
            # The plant casts a seed every hour in sim time (60 seconds * 60 minutes)
            if self.totalSeedsDropped >= 6:
                self.Death()
            if self.timeSinceLastSeedDroped == 3600:
                for i in range(0, random.randint(1, self.dataParser.MaxSeedNumber)):
                    self.ReleaseSeed()
                self.timeSinceLastSeedDroped = 0
            else:
                self.timeSinceLastSeedDroped += 1

    def CastSeedLocation(self):
        valid = False
        while not valid:
            radius = random.random() * self.dataParser.MaxSeedCastDistance
            angle = random.random() * 2 * math.pi
            if(int(self.X + radius * math.cos(angle)) > 1000 or int(self.X + radius * math.cos(angle)) < 0 or
               int(self.Y + radius * math.sin(angle)) > 750 or int(self.Y + radius * math.sin(angle)) < 0):
                valid = False
            else:
                valid = True
        return (int(self.X + radius * math.cos(angle)),
                int(self.Y + radius * math.sin(angle)))
