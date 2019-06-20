# Import needed libraries
from pydispatch import dispatcher
import DataParser
import EventSignals
from enum import Enum
from random import random, choice
import random
import math
import operator


def checkCollision(x1, x2, y1, y2, circleX, circleY, radius):

    if pointCircleCollision(x1, y1, circleX, circleY, radius) is True or pointCircleCollision(x2, y2, circleX, circleY, radius) is True:
        return True

    length = math.hypot(x2 - x1, y2 - y1)
    if length == 0:
        print('wtf')
    dot = (((circleX - x1) * (x2 - x1)) + ((circleY - y1) * (y2 - y1))) / pow(length + 0.0000001, 2)

    closestX = x1 + (dot * (x2 - x1))
    closestY = y1 + (dot * (y2 - y1))

    onSegment = linePointCollision(x1, x2, y1, y2, closestX, closestY)

    if not onSegment:
        return False

    distance = math.hypot(circleX - closestX, circleY - closestY)

    if(distance <= radius):
        return True
    else:
        return False


def pointCircleCollision(px, py, cx, cy, r):
    distance = math.hypot(cx - px, cy - py)

    if(distance <= r):
        return True
    else:
        return False


def linePointCollision(x1, x2, y1, y2, px, py):
    d1 = math.hypot(x1 - px, y1 - py)
    d2 = math.hypot(x2 - px, y2 - py)

    lineLength = math.hypot(x2 - x1, y2 - y1)

    buffer = 0.1

    if(d1 + d2 >= lineLength - buffer and d1 + d2 <= lineLength + buffer):
        return True
    else:
        return False


class GrazerLifeStages(Enum):
    Adult = 0


class Grazer():

    def __init__(self, X, Y, energyLevel, lifestage=GrazerLifeStages.Adult):

        # Getting data parser instance
        self.dataParser = DataParser.DataParser.getInstance()

        # Initializing world position
        self.X = X
        self.Y = Y

        # Initializing energy level
        self.EnergyLevel = energyLevel

        # Initialize Lifestage
        self.LifeStage = lifestage

        # Initialize Current Direction to 0 degrees
        self.CurrDirection = 0

        # Initialize Current Speed
        self.CurrSpeed = 0

        # Get Max Speed
        self.MaxSpeed = self.dataParser.GrazerMaxSpeed

        # Initialize isSlowingDown boolean to False
        self.isSlowingDown = False

        # Initialize Time at Max Speed to 0, given in minutes SimTime
        self.TimeAtMaxSpeed = 0
        self.TimeGoingRandomDirection = 0
        self.DistanceTraveled = 0

        # Initialize targetLocked to False
        self.targetLocked = False

        # Initialize nearby organisms to None
        self.targetFoodSource = None
        self.closestPredator = None

        # Initialize nerby organisms lists to empty lists
        self.predatorsNearby = []
        self.plantsNearby = []
        self.obstaclesNearby = []

        # Initialize Living
        self.Alive = True

        # Initialize time spent eating current plant in seconds
        self.TimeEating = 0

        # Initialize bools for next action
        self.IsEating = False
        self.IsPredatorNearby = False
        self.IsWeak = False

    # Set ID String for current Grazer
    def SetId(self, idStr):
        self.Id = idStr

    # Set Energy Level for current Grazer
    def SetEnergyLevel(self, energyLevel):
        self.EnergyLevel = energyLevel
        if(self.EnergyLevel >= self.dataParser.GrazerEnergyToReproduce):
            self.Reproduce()
        elif(self.EnergyLevel <= 25 and self.EnergyLevel > 0):
            self.IsWeak
        elif (self.EnergyLevel <= 0):
            self.Death()

    # Set Location of current Grazer
    def SetLocation(self, x, y):
        # Set the x position
        self.X = x
        # Set the y position
        self.Y = y

    # Set Life Stage for current Grazer
    def SetLifeStage(self, lifeStage):
        self.LifeStage = lifeStage

    # Set Speed of current Grazer
    def SetSpeed(self):
        # set max speed
        if self.IsWeak:
            self.MaxSpeed = 10
        else:
            self.MaxSpeed = self.dataParser.GrazerMaxSpeed

        if self.IsEating:  # if you're eating you can't be running
            self.CurrSpeed = 0
        # If predator is still speeding up to MaxSpeed and not Tired
        elif self.CurrSpeed < self.MaxSpeed and not self.isSlowingDown:
            # grazers reach their max speed after 30 seconds (abitrarily set)
            self.CurrSpeed += self.MaxSpeed / 30
        else:  # but slow down soon after
            if self.TimeAtMaxSpeed >= self.dataParser.GrazerMaxSpeedTime:
                self.CurrSpeed = self.MaxSpeed * 0.75
            else:
                self.TimeAtMaxSpeed += 1 / 60  # Increase TimeAtMaxSpeed by 1 second SimTime

    def GetRandomDirection(self):
        return random.randint(0, 360)

    # Change direction by 180 degrees
    def TurnAround(self):
        self.CurrDirection = int(
            self.CurrDirection + 180) if self.CurrDirection <= 180 else int(self.CurrDirection - 180)

    # Change direction by 90 degrees
    def TurnRight(self):
        self.CurrDirection = int(self.CurrDirection + 90)
        self.CurrDirection = self.Clamp(self.CurrDirection, 0, 360)

    # Change direction by 90 degrees
    def TurnLeft(self):
        self.CurrDirection = int(self.CurrDirection - 90)
        self.CurrDirection = self.Clamp(self.CurrDirection, 0, 360)

    def Clamp(self, value, start, end):
        width = end - start
        offset = value - start
        return (offset - (math.floor(offset / width) * width)) + start

    # Move current Grazer at CurrentSpeed in CurrentDirection (direction given as angle)
    def Move(self, angle):

        # Get obstacles that you would hit
        for obstacle in self.obstaclesNearby:
            if checkCollision(self.X, self.X + (self.CurrSpeed *
                                                round(math.cos(math.radians(angle)), 2)) / 60,
                              self.Y, self.Y + (self.CurrSpeed *
                                                round(math.sin(math.radians(angle)), 2)) / 60,
                              obstacle.X, obstacle.Y, obstacle.Diameter / 2) is True:
                self.X += (15 * round(math.cos(math.radians(-angle)), 2))
                self.Y += (15 * round(math.sin(math.radians(-angle)), 2))
                self.TurnRight() if random.randint(0, 1) == 0 else self.TurnLeft()

        # If Predator X position withing world bounds
        if self.X >= 0 and self.X <= 1000:
            # Increase X position by [CurrentSpeed * cos(CurrentAngle)] / 60 (CurrSpeed given in DU per minute)
            self.X += (self.CurrSpeed *
                       round(math.cos(math.radians(angle)), 2)) / 60
        elif self.X < 0:  # if predator goes out-of-bounds place in-bounces and turn around
            self.X = 0
            self.TimeGoingRandomDirection = 180
        elif self.X > 1000:  # if predator goes out-of-bounds place in-bounces and turn around
            self.X = 1000
            self.TimeGoingRandomDirection = 180

        # If Predator Y position withing world bounds
        if self.Y >= 0 and self.Y <= 750:
            # Increase Y position by [CurrentSpeed * sin(CurrentAngle)] / 60 (CurrSpeed given in DU per minute)
            self.Y += (self.CurrSpeed *
                       round(math.sin(math.radians(angle)), 2)) / 60
        elif self.Y < 0:  # if predator goes out-of-bounds place in-bounces and turn around
            self.Y = 0
            self.TimeGoingRandomDirection = 180
        elif self.Y > 750:  # if predator goes out-of-bounds place in-bounces and turn around
            self.Y = 750
            self.TimeGoingRandomDirection = 180

        # Update the distance traveled this tick
        distanceTraveled = self.CurrSpeed / 60
        energyExpended = distanceTraveled / 5

        self.SetEnergyLevel(
            self.EnergyLevel - (energyExpended * self.dataParser.GrazerEnergyOutputRate))

    # Returns the angle between two organisms

    def GetAngle(self, Y2, Y1, X2, X1):
        angle = int(math.degrees(math.atan2(Y2 - Y1, X2 - X1)))
        return angle if angle >= 0 else angle + 360

    def GetAngleToCenter(self):
        centerX = self.dataParser.WorldWidth / 2
        centerY = self.dataParser.WorldHeight / 2
        angle = int(math.degrees(math.atan2(centerY - self.Y, centerX - self.X)))
        return angle if angle >= 0 else angle + 360

    # Returns the closest organism to current Grazer given organismList
    def GetClosestPlant(self, organismList, obstacleList):
        # list to contain distances of each nearby organism
        organismDistances = []
        obstacleDistances = []
        # populate list with each nearby organism and their distance to current Predator
        for organism in organismList:
            if(math.hypot(self.X - organism.X, self.Y - organism.Y) <= 150):
                organismDistances.append(
                    {
                        'organism': organism,
                        'distance': math.hypot(self.X - organism.X, self.Y - organism.Y)
                    }
                )

        for obstacle in obstacleList:
            if(math.hypot(self.X - obstacle.X, self.Y - obstacle.Y) <= 150):
                obstacleDistances.append(
                    {
                        'obstacle': obstacle,
                        'distance': math.hypot(self.X - obstacle.X, self.Y - obstacle.Y)
                    }
                )

        # Sort list of distance dictonaries by distance key
        organismDistances.sort(key=operator.itemgetter('distance'))
        obstacleDistances.sort(key=operator.itemgetter('distance'))

        for organism in organismDistances:
            isBlocked = False
            for obstacle in obstacleDistances:
                # if the obstacle is further away it's not going to block
                if obstacle['distance'] > organism['distance']:
                    continue
                else:
                    if checkCollision(self.X, organism['organism'].X, self.Y, organism['organism'].Y,
                                      obstacle['obstacle'].X, obstacle['obstacle'].Y,
                                      obstacle['obstacle'].Diameter / 2) is True:
                        isBlocked = True  # if the organism is blocked continue to the next one
                        break
            if isBlocked is True:
                continue
            else:
                return organism['organism']

        # if the previous block didn't return that means there are no nearby or they
        # are all blocked
        return None

        # # if organismDistances is not empty return organism in the first element
        # if organismDistances:
        #     return organismDistances[0]['organism']
        # else:  # if organismDistances is empty return none
        #     return None

    # Returns the closest predator to current Grazer given organismList
    def GetClosestPredator(self, organismList, obstacleList):
        # list to contain distances of each nearby organism
        organismDistances = []
        obstacleDistances = []

        # populate list with each nearby organism and their distance to current Predator
        for organism in organismList:
            if(math.hypot(self.X - organism.X, self.Y - organism.Y) <= 25):
                organismDistances.append(
                    {
                        'organism': organism,
                        'distance': math.hypot(self.X - organism.X, self.Y - organism.Y)
                    }
                )

        for obstacle in obstacleList:
            if(math.hypot(self.X - obstacle.X, self.Y - obstacle.Y) <= 25):
                obstacleDistances.append(
                    {
                        'obstacle': obstacle,
                        'distance': math.hypot(self.X - obstacle.X, self.Y - obstacle.Y)
                    }
                )

        # Sort list of distance dictonaries by distance key
        organismDistances.sort(key=operator.itemgetter('distance'))
        obstacleDistances.sort(key=operator.itemgetter('distance'))

        for organism in organismDistances:
            isBlocked = False
            for obstacle in obstacleDistances:
                # if the obstacle is further away it's not going to block
                if obstacle['distance'] > organism['distance']:
                    continue
                else:
                    if checkCollision(self.X, organism['organism'].X, self.Y, organism['organism'].Y,
                                      obstacle['obstacle'].X, obstacle['obstacle'].Y,
                                      obstacle['obstacle'].Diameter / 2) is True:
                        isBlocked = True  # if the organism is blocked continue to the next one
                        break
            if isBlocked is True:
                continue
            else:
                return organism['organism']

        return None

    def Reproduce(self):
        newGrazer = Grazer(
            self.X + 15 * math.cos(math.radians(random.randint(0, 360))),
            self.Y + 15 * math.sin(math.radians(random.randint(0, 360))),
            self.EnergyLevel / 2
        )
        dispatcher.send(signal=EventSignals.grazerCreation,
                        sender=self.Id, newGrazer=newGrazer)

        newGrazer = Grazer(
            self.X + 15 * math.cos(math.radians(random.randint(0, 360))),
            self.Y + 15 * math.sin(math.radians(random.randint(0, 360))),
            self.EnergyLevel / 2
        )

        dispatcher.send(signal=EventSignals.grazerCreation,
                        sender=self.Id, newGrazer=newGrazer)
        # setting the energy low so they don't just sit there and pop out grazers every tick
        self.SetEnergyLevel(10)

    # When Grazer is eaten or runs out of EU, it dies and is removed from the simulation
    def Death(self):
        self.Alive = False
        dispatcher.send(signal=EventSignals.grazerDeath, sender=self.Id)

    # Current Grazer eats targetOrganism
    def EatOrganism(self, targetOrganism):
        if self.TimeEating < 600 and targetOrganism is not None:
            self.TimeEating += 1
            if(self.TimeEating % 60 == 0):
                self.SetEnergyLevel(self.EnergyLevel +
                                    self.dataParser.GrazerEnergyInputRate)

        else:
            self.TimeEating = 0
            # Once you're done eating turn off the lock target
            self.targetLocked = False  # lock-off target
            self.targetFoodSource = None  # reset foodSource to None
            # Send signal to WorldData to remove targetOrganism from the global list
            if(targetOrganism is not None):
                dispatcher.send(signal=EventSignals.plantDeath,
                                sender=targetOrganism.Id)

    # Return Target Food Source for current predator given list of nearby organisms
    def FindTargetFoodSource(self, organismList, obstacleList):

        # if organisms exist in organismList
        # set closest organism as targetFoodSource for current grazer
        self.targetFoodSource = self.GetClosestPlant(
            organismList, obstacleList)

        # if targetFoodSource found lock-on to target
        # and set direction of grazer toward targetFoodSource
        if self.targetFoodSource is not None:
            self.targetLocked = True

    def FindNearbyPredator(self, organismList, obstacleList):

        # if organisms exist in organismList
        # set closest organism as targetFoodSource for current grazer
        self.closestPredator = self.GetClosestPredator(
            organismList, obstacleList)

        # if targetFoodSource found lock-on to target
        # and set direction of Predator away from the predator
        if self.closestPredator is not None:
            self.IsPredatorNearby = True

    def SenseOrganism(self):
        # Clear lists of nearby organisms
        self.predatorsNearby = []
        self.plantsNearby = []
        self.obstaclesNearby = []

        # Send signal to WorldData to handle predator Sensing
        # Populates predatorsNearby and grazersNearby with respective organisms with 150 DU radius of current Predator
        dispatcher.send(signal=EventSignals.grazerSensing, sender=self)

        # if Grazer has no current target, search for closest food source
        if not self.targetLocked:
            self.FindTargetFoodSource(self.plantsNearby, self.obstaclesNearby)

        self.FindNearbyPredator(self.predatorsNearby, self.obstaclesNearby)

    # Selects the next action of current graazer:
    def PerformNextAction(self):
        # Check for nearby plants and predators
        self.SenseOrganism()

        # If there is a nearby predator RUN
        if self.IsPredatorNearby and self.closestPredator is not None:
            self.IsEating = False
            self.targetFoodSource = None
            self.TimeGoingRandomDirection = 0
            # get the angle to the predator then do a 180
            self.CurrDirection = self.GetAngle(
                self.closestPredator.Y, self.Y, self.closestPredator.X, self.X)
            self.TurnAround()
            # Update Speed of current Grazer
            self.SetSpeed()
            self.Move(self.CurrDirection)
        # if targetFoodSource is found, check if within 5 DU of it and eat it
        elif self.targetFoodSource is not None:
            self.TimeGoingRandomDirection = 0
            if math.hypot(self.X - self.targetFoodSource.X, self.Y - self.targetFoodSource.Y) <= (self.targetFoodSource.Diameter / 2) + 5:
                self.IsEating = True
                self.EatOrganism(self.targetFoodSource)
            else:  # If not move towards it
                self.IsEating = False
                self.CurrDirection = self.GetAngle(
                    self.targetFoodSource.Y, self.Y, self.targetFoodSource.X, self.X)
                # Update Speed of current Predator
                self.SetSpeed()
                # Update current X and Y position based on Current Direction
                self.Move(self.CurrDirection)
        else:   # If no plants are predators are around move till you find one
            self.IsEating = False
            self.targetFoodSource = None
            self.TimeGoingRandomDirection += 1

            if self.TimeGoingRandomDirection >= 180:
                self.CurrDirection = random.randint(0, 360)
                self.TimeGoingRandomDirection = 0

            # Update Speed of current Predator
            self.SetSpeed()
            # Update current X and Y position based on Current Direction
            self.Move(self.CurrDirection)
