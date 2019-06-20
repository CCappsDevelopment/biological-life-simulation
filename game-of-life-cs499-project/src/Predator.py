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


class PredatorLifeStages(Enum):
    Adult = 0
    MatingAdult = 1


# Defining our Class
class Predator():

    def __init__(self, X, Y, energyLevel, genotype, lifestage=PredatorLifeStages.Adult):

        self.dataParser = DataParser.DataParser.getInstance()
        # Initialize xposition
        self.X = X
        # Initialize yposition
        self.Y = Y
        # Initialize Energy Level
        self.EnergyLevel = energyLevel
        # Initialize Lifestage
        self.LifeStage = lifestage
        # Initialize Genotype
        self.Genotype = genotype
        # Initialize Current Direction to 0 degrees
        self.CurrDirection = 0
        # Initialize Current Speed
        self.CurrSpeed = 0
        # Get Max Speed based on Genotype
        self.MaxSpeed = self.GetMaxSpeed()

        self.distanceSinceEnergyLoss = 0
        # Initialize isSlowingDown boolean to False
        self.isSlowingDown = False
        # Initialize Time at Max Speed to 0, given in minutes SimTime
        self.TimeAtMaxSpeed = 0
        self.TimeGoingRandomDirection = 0
        # Initialize targetLocked to False
        self.targetLocked = False
        # Initialize targetFoodSource to None
        self.targetFoodSource = None

        self.foodSourceType = None
        # Initialize targetMate as None
        self.targetMate = None
        self.isGestating = False
        self.TimeGestating = 0
        self.LastMate = None
        self.Parents = []
        self.Children = []
        self.TimeSinceBirth = 0
        self.TimeSinceLastMated = 0
        # Initialize grazersNearby to empty list
        self.grazersNearby = []
        # Initialize predatorsNearby to empty list
        self.predatorsNearby = []
        self.obstaclesNearby = []
        # Initialize Mating
        self.CanMate = False
        # Initialize Living
        self.Alive = True

    # Change direction by 180 degrees
    def TurnAround(self):
        self.CurrDirection = int(self.CurrDirection + 180) if self.CurrDirection <= 180 else int(self.CurrDirection - 180)
        self.TimeGoingRandomDirection = 0

    # Change direction by 90 degrees
    def TurnRight(self):
        self.targetFoodSource = None
        self.TimeGoingRandomDirection = 0
        self.CurrDirection = int(self.CurrDirection + 90)
        self.CurrDirection = self.Clamp(self.CurrDirection, 0, 360)

    # Change direction by 90 degrees
    def TurnLeft(self):
        self.targetFoodSource = None
        self.TimeGoingRandomDirection = 0
        self.CurrDirection = int(self.CurrDirection - 90)
        self.CurrDirection = self.Clamp(self.CurrDirection, 0, 360)

    def Clamp(self, value, start, end):
        width = end - start
        offset = value - start
        return (offset - (math.floor(offset / width) * width)) + start

    # Set ID String for current Predator
    def SetId(self, idStr):
        self.Id = idStr

    # Set Energy Level for current Predator
    def SetEnergyLevel(self, energyLevel):
        self.EnergyLevel = energyLevel
        if self.EnergyLevel > 1000:
            self.EnergyLevel = 1000

    def SetParents(self, parent1, parent2):
        self.Parents = [parent1, parent2]

    # Set Location of current Predator
    def SetLocation(self, x, y):
        # Set the x position
        self.X = x
        # Set the y position
        self.Y = y

    # Set Life Stage for current Predator
    def SetLifeStage(self, lifeStage):
        # Life stage can be 'Adult', & 'MatingAdult' from enum PredatorLifeStages
        self.LifeStage = lifeStage

    # Set Genotype of current Predaot
    def SetGenotype(self, parent1, parent2):
        # print("Parent 1: ", parent1.Genotype, "  Parent 2: ", parent2.Genotype)
        for i in range(0, 3):
            gen = random.choice([parent1.Genotype[i][:1], parent2.Genotype[i][:1]])
            gen += random.choice([parent1.Genotype[i][1:], parent2.Genotype[i][1:]])
            self.Genotype[i] = gen
        # print("Genotype: ", self.Genotype)

    # Set Speed of current Predator
    def SetSpeed(self):
        # If predator is still speeding up to MaxSpeed and not Tired
        if self.CurrSpeed < self.MaxSpeed and not self.isSlowingDown:
            self.CurrSpeed += self.MaxSpeed / 30  # increase speed by 1 DU every 15 seconds SimTime
        else:  # if Predator reaches MaxSpeed slow to a stop
            if self.dataParser.PredatorMaxSpeedTime <= self.TimeAtMaxSpeed:
                if self.CurrSpeed > 0:
                    self.CurrSpeed -= 1 / 15  # decrease speed by 1 DU every 15 seconds SimTime
                    self.isSlowingDown = True  # Predator is now slowing down
                else:
                    self.isSlowingDown = False  # Predator is no longer slowing down, can start gaining speed again
                    self.TimeAtMaxSpeed = 0  # reset TimeAtMaxSpeed
            else:
                self.TimeAtMaxSpeed += 1 / 60  # Increase TimeAtMaxSpeed by 1 second SimTime (TimeAtMaxSpeed given in minutes)

    # Move current Predator at CurrentSpeed in CurrentDirection (direction given as angle)
    def Move(self, angle):
        for obstacle in self.obstaclesNearby:
            if checkCollision(
                self.X,
                self.X + (self.MaxSpeed * round(math.cos(math.radians(angle)), 2)) / 60,
                self.Y,
                self.Y + (self.MaxSpeed * round(math.sin(math.radians(angle)), 2)) / 60,
                obstacle.X,
                obstacle.Y,
                obstacle.Diameter / 2
            ) is True:
                self.X += (15 * round(math.cos(math.radians(-angle)), 2))
                self.Y += (15 * round(math.sin(math.radians(-angle)), 2))
                self.TurnRight() if random.randint(0, 1) == 0 else self.TurnLeft()

        # If Predator X position withing world bounds
        if self.X >= 0 and self.X <= 1000:
            # Increase X position by [CurrentSpeed * cos(CurrentAngle)] / 60 (CurrSpeed given in DU per minute)
            self.X += (self.CurrSpeed * round(math.cos(math.radians(angle)), 2)) / 60
        elif self.X < 0:  # if predator goes out-of-bounds place in-bounces and turn around
            self.X = 0
            self.CurrDirection = self.GetAngleToCenter()
        elif self.X > 1000:  # if predator goes out-of-bounds place in-bounces and turn around
            self.X = 1000
            self.CurrDirection = self.GetAngleToCenter()

        # If Predator Y position withing world bounds
        if self.Y >= 0 and self.Y <= 750:
            # Increase Y position by [CurrentSpeed * sin(CurrentAngle)] / 60 (CurrSpeed given in DU per minute)
            self.Y += (self.CurrSpeed * round(math.sin(math.radians(angle)), 2)) / 60
        elif self.Y < 0:  # if predator goes out-of-bounds place in-bounces and turn around
            self.Y = 0
            self.CurrDirection = self.GetAngleToCenter()
        elif self.Y > 750:  # if predator goes out-of-bounds place in-bounces and turn around
            self.Y = 750
            self.CurrDirection = self.GetAngleToCenter()

        # Update the distance traveled this tick
        distanceTraveled = self.CurrSpeed / 60
        energyExpended = distanceTraveled / 5
        self.SetEnergyLevel(self.EnergyLevel - energyExpended * self.dataParser.PredatorEnergyOutputRate)

    # Returns X and Y positions for current Predator
    def GetLocation(self):
        # Return the x and y position
        return self.X, self.Y

    # Returns the amount of Energy Units of current Predator
    def GetEnergyLevel(self):
        return self.EnergyLevel

    # Returns LifeStage of current Predator
    def GetLifeStage(self):
        # Return the life stage
        return self.LifeStage

    # Returns the MaxSpeed for current Predator based on given Genotype
    def GetMaxSpeed(self):
        if self.Genotype[2] == 'FF':
            return self.dataParser.PredatorMaxSpeedHOD
        elif self.Genotype[2] == 'Ff' or self.Genotype[2] == 'fF':
            return self.dataParser.PredatorMaxSpeedHED
        else:
            return self.dataParser.PredatorMaxSpeedHOR

    # Returns the angle between two organisms
    def GetAngle(self, Y2, Y1, X2, X1):
        angle = int(math.degrees(math.atan2(Y2 - Y1, X2 - X1)))
        return angle if angle >= 0 else angle + 360

    def GetAngleToCenter(self):
        centerX = self.dataParser.WorldWidth / 2
        centerY = self.dataParser.WorldHeight / 2
        angle = int(math.degrees(math.atan2(centerY - self.Y, centerX - self.X)))
        return angle if angle >= 0 else angle + 360

    # Returns the closest organism to current Predator given organismList
    def GetClosestOrganism(self, organismList, obstacleList):
        # list to contain distances of each nearby organism
        organismDistances = []
        obstacleDistances = []
        # populate list with each nearby organism and their distance to current Predator
        for organism in organismList:
            organismDistances.append(
                {
                    'organism': organism,
                    'distance': math.hypot(self.X - organism.X, self.Y - organism.Y)
                }
            )
        for obstacle in obstacleList:
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
                    if checkCollision(
                        self.X,
                        organism['organism'].X,
                        self.Y,
                        organism['organism'].Y,
                        obstacle['obstacle'].X,
                        obstacle['obstacle'].Y,
                        obstacle['obstacle'].Diameter / 2
                    ) is True:
                        isBlocked = True  # if the organism is blocked continue to the next one
                        break
            if isBlocked is True:
                continue
            else:
                return organism['organism']

        # if the previous block didn't return that means there are no nearby or they
        # are all blocked
        return None

    # When Predator is at MatingAdult stage set CanMate to True
    def ReadyToMate(self):
        if self.Alive and self.LifeStage == PredatorLifeStages.MatingAdult:
            self.CanMate = True

    # When Predator is eaten or runs out of EU, it dies and is removed from the simulation
    def Death(self):
        # The Predator has been killed in combat or has run out of energy
        self.Alive = False
        dispatcher.send(signal=EventSignals.predatorDeath, sender=self.Id)

    # Current Predator eats targetGrazer
    def EatGrazer(self, targetGrazer):
        strengthCheck = random.random()
        if self.Genotype[1] == "SS":
            if strengthCheck > 0.95:
                # Send signal to WorldData to remove targetGrazer from the global list
                dispatcher.send(signal=EventSignals.organismDeath, sender=targetGrazer)
                self.SetEnergyLevel(self.EnergyLevel + (targetGrazer.EnergyLevel * 0.9))
                self.TimeGoingRandomDirection = 180
            else:
                pass
        elif self.Genotype[1] == "Ss" or self.Genotype[1] == "sS":
            if strengthCheck > 0.75:
                # Send signal to WorldData to remove targetGrazer from the global list
                dispatcher.send(signal=EventSignals.organismDeath, sender=targetGrazer)
                self.SetEnergyLevel(self.EnergyLevel + (targetGrazer.EnergyLevel * 0.9))
                self.TimeGoingRandomDirection = 180
            else:
                pass
        else:
            if strengthCheck > 0.5:
                # Send signal to WorldData to remove targetGrazer from the global list
                dispatcher.send(signal=EventSignals.organismDeath, sender=targetGrazer)
                self.SetEnergyLevel(self.EnergyLevel + (targetGrazer.EnergyLevel * 0.9))
                self.TimeGoingRandomDirection = 180
            else:
                pass

    def FightPredator(self, targetPredator):
        preyDefeated = False
        strengthCheck = random.random()
        if self.Genotype[1] == "SS":
            if targetPredator.Genotype[1] == self.Genotype[1]:
                if random.random() >= 0.5:
                    if strengthCheck > 0.5:
                        preyDefeated = True
                else:
                    self.TimeGoingRandomDirection = 180
                    return
            elif targetPredator.Genotype[1] == "Ss" or targetPredator.Genotype[1] == "sS":
                if strengthCheck > 0.75:
                    preyDefeated = True
            else:
                if strengthCheck > 0.95:
                    preyDefeated = True
        elif self.Genotype[1] == "Ss" or self.Genotype[1] == "sS":
            if targetPredator.Genotype[1] == self.Genotype[1]:
                if random.random() >= 0.5:
                    if strengthCheck > 0.5:
                        preyDefeated = True
                else:
                    self.TimeGoingRandomDirection = 180
                    return
            elif targetPredator.Genotype[1] == "SS":
                if strengthCheck > 0.25:
                    preyDefeated = True
            else:
                if strengthCheck > 0.75:
                    preyDefeated = True
        else:
            if targetPredator.Genotype[1] == self.Genotype[1]:
                if random.random() >= 0.5:
                    if strengthCheck > 0.5:
                        preyDefeated = True
                else:
                    self.TimeGoingRandomDirection = 180
                    return
            elif targetPredator.Genotype[1] == "Ss" or targetPredator.Genotype[1] == "sS":
                if strengthCheck > 0.25:
                    preyDefeated = True
            else:
                if strengthCheck > 0.05:
                    preyDefeated = True

        if preyDefeated:
            dispatcher.send(signal=EventSignals.organismDeath, sender=targetPredator)
            self.SetEnergyLevel(self.EnergyLevel + (targetPredator.EnergyLevel * 0.9))
            self.TimeGoingRandomDirection = 180
        else:
            targetPredator.SetEnergyLevel(targetPredator.EnergyLevel + (self.EnergyLevel * 0.9))
            self.Death

    def Mate(self, targetMate):
        if targetMate != self.LastMate:
            # print(self, " mated with ", targetMate)
            self.isGestating = True
            self.LastMate = targetMate
            self.TimeGoingRandomDirection = 180
            self.TimeSinceLastMated = 0

    def GiveBirth(self):
        for x in range(0, random.randint(1, self.dataParser.PredatorMaxOffspring)):
            newPredator = Predator(
                self.X + 25 * math.cos(math.radians(random.randint(0, 360))),
                self.Y + 25 * math.sin(math.radians(random.randint(0, 360))),
                self.dataParser.PredatorOffspringEnergyLevel,
                ['A', 'S', 'F']
            )
            dispatcher.send(signal=EventSignals.predatorCreation, sender=self.Id, parent1=self, parent2=self.LastMate, newPredator=newPredator)
            self.Children.append(newPredator)
        self.isGestating = False
        self.TimeGestating = 0
        self.SetEnergyLevel(self.EnergyLevel / 2)

    # Return Target Food Source for current predator given list of nearby organisms
    def FindTargetFoodSource(self, organismList, obstacleList):
        # if organisms exist in organismList
        # set closest organism as targetFoodSource for current Predator
        self.targetFoodSource = self.GetClosestOrganism(organismList, obstacleList)
        # if targetFoodSource found lock-on to target
        # and set direction of Predator toward targetFoodSource
        if self.targetFoodSource is not None:
            if self.targetFoodSource in self.Parents or self.targetFoodSource in self.Children:
                if self.TimeSinceBirth >= 3600:
                    self.targetLocked = True
                    self.CurrDirection = self.GetAngle(self.targetFoodSource.Y, self.Y, self.targetFoodSource.X, self.X)
                else:
                    self.targetFoodSource = None
                    self.targetLocked = False
            else:
                self.targetLocked = True
                self.CurrDirection = self.GetAngle(self.targetFoodSource.Y, self.Y, self.targetFoodSource.X, self.X)

    # Main Sensing Function for current Predator
    # Take in organismType (Either: 'foodSource' or 'mate' )
    # if detecting foodsource check in 150 DU line of sight for targetFoodSource (based on Predator's Genotype)
    # when foodSource located move toward it until within 25 DU of targetOrganism,
    # Eat targetFoodSource and begin looking for another target
    def SenseOrganism(self, organismType):
        # Clear lists of nearby organisms
        self.predatorsNearby = []
        self.grazersNearby = []
        self.obstaclesNearby = []
        # Remove current target foodsource and lock-off target
        # self.targetFoodSource = None
        # self.targetLocked = False
        # Send signal to WorldData to handle predator Sensing
        # Populates predatorsNearby and grazersNearby with respective organisms with 150 DU radius of current Predator
        dispatcher.send(signal=EventSignals.predatorSensing, sender=self)

        # if Predator has no current target, search for closest food source (based on Genotype)
        if not self.targetLocked:
            if organismType == "foodSource":  # if sensing for foodSource
                if self.Genotype[0] == "AA":  # Very Aggressive predator targets predator first, if none nearby targets grazer
                    self.FindTargetFoodSource(self.predatorsNearby, self.obstaclesNearby)
                    self.foodSourceType = "predator"
                    if self.targetFoodSource is None:
                        self.FindTargetFoodSource(self.grazersNearby, self.obstaclesNearby)
                        self.foodSourceType = "grazer"
                elif self.Genotype[0] == "Aa" or self.Genotype[0] == "aA":  # Moderately Aggressive predator targets grazer first, if none nearby targets predator
                    self.FindTargetFoodSource(self.grazersNearby, self.obstaclesNearby)
                    self.foodSourceType = "grazer"
                    if self.targetFoodSource is None:
                        self.FindTargetFoodSource(self.predatorsNearby, self.obstaclesNearby)
                        self.foodSourceType = "predator"
                elif self.Genotype[0] == "aa":  # Non-Aggressive predator targets grazer first, if predator nearby, turns around
                    self.FindTargetFoodSource(self.grazersNearby, self.obstaclesNearby)
                    self.foodSourceType = "grazer"
                    if self.predatorsNearby and self.targetFoodSource is None:
                        closestPredator = self.GetClosestOrganism(self.predatorsNearby, self.obstaclesNearby)
                        if closestPredator is not None:
                            self.CurrDirection = (- self.GetAngle(closestPredator.Y, self.Y, closestPredator.X, self.X)) + 360
            elif organismType == "mate":  # if sensing for mate
                # Remove current targetFoodSource and lock-off of it
                self.targetFoodSource = None
                self.targetLocked = False
                # list for potential mates
                self.potentialMates = []
                # if any Predators nearby is able to mate, add it to the list
                for predator in self.predatorsNearby:
                    if predator.CanMate:
                        self.potentialMates.append(predator)

                self.targetMate = self.GetClosestOrganism(self.potentialMates, self.obstaclesNearby)
                # if Mate located, lock-on to Mate and set direction towards them
                if self.targetMate is not None:
                    self.TimeGoingRandomDirection = 0
                    self.targetLocked = True
                    self.CurrDirection = self.GetAngle(self.targetMate.Y, self.Y, self.targetMate.X, self.X)

    # Updates lifestage of current Predator
    # if current EnergyLevel is above 500 EU, Predator becomes MatingAdult; Adult, otherwise
    def UpdateLifeStage(self):
        # Updating LiveStage
        if self.EnergyLevel >= self.dataParser.PredatorEnergyToReproduce:
            self.LifeStage = PredatorLifeStages.MatingAdult
            self.ReadyToMate()  # Set CanMate to True
        else:
            self.LifeStage = PredatorLifeStages.Adult

    # Selects the next action of current predator:
    # Updates Life Stage, Sets Speed, then finds either target foodSource or targetMate
    # Depending on current Predator's lifeStage
    def PerformNextAction(self):
        self.TimeSinceBirth += 1
        # Update LifeStage before we move on
        self.UpdateLifeStage()
        # Update Speed of current Predator
        self.SetSpeed()

        if self.isGestating:
            self.TimeGestating += 1 / 60
            if self.TimeGestating >= self.dataParser.PredatorGestationPeriodDays:
                self.isGestating = False
                self.GiveBirth()

        # if Adult predator, search for food source; if mating adult, seek mate
        if self.LifeStage == PredatorLifeStages.Adult:
            self.SenseOrganism("foodSource")
        elif self.LifeStage == PredatorLifeStages.MatingAdult:
            if not self.isGestating:
                self.SenseOrganism("mate")
                if self.targetMate is None or self.TimeSinceLastMated >= 3600:
                    self.SenseOrganism("foodSource")
            else:
                if self.TimeSinceLastMated >= 3600:
                    self.SenseOrganism("foodSource")


        # if targetFoodSource is found, check if within 25 DU of it and eat it
        if self.targetFoodSource and self.targetFoodSource.Alive:
            self.TimeGoingRandomDirection = 0
            self.CurrDirection = self.GetAngle(self.targetFoodSource.Y, self.Y, self.targetFoodSource.X, self.X)
            if math.hypot(self.X - self.targetFoodSource.X, self.Y - self.targetFoodSource.Y) <= 20:
                if self.foodSourceType == "grazer":
                    self.EatGrazer(self.targetFoodSource)
                elif self.foodSourceType == "predator":
                    self.FightPredator(self.targetFoodSource)
                self.targetLocked = False  # lock-off target
                self.targetFoodSource = None  # reset foodSource to None
                self.foodSourceType = None
        # if targetMate is found, check if within 25 DU of it and mate
        elif self.targetMate and self.targetMate.Alive:
            self.TimeGoingRandomDirection = 0
            self.CurrDirection = self.GetAngle(self.targetMate.Y, self.Y, self.targetMate.X, self.X)
            if math.hypot(self.X - self.targetMate.X, self.Y - self.targetMate.Y) <= 25:
                self.Mate(self.targetMate)
                self.targetLocked = False  # lock-off target
                self.targetMate = None
        else:
            self.targetLocked = False  # lock-off target
            self.foodSourceType = None
            self.targetFoodSource = None  # reset foodSource to None
            self.targetMate = None
            self.TimeGoingRandomDirection += 1
            if self.TimeGoingRandomDirection >= 180:
                if (self.X <= 700 and self.X >= 300) and (self.Y <= 100 and self.Y >= 650):
                    self.CurrDirection = self.GetAngleToCenter()
                else:
                    self.CurrDirection = random.randint(0, 360)
                self.TimeGoingRandomDirection = 0
            if self.TimeSinceBirth <= 3600 and self.Parents:
                if math.hypot(self.X - self.Parents[0].X, self.Y - self.Parents[0].Y) <= 200:
                    self.CurrDirection = (-self.GetAngle(self.Parents[0].Y, self.Y, self.Parents[0].X, self.X)) + 360

        # Update current X and Y position based on Current Direction
        self.Move(self.CurrDirection)

        if self.EnergyLevel <= 0:
            self.Death()
