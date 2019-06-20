from DataParser import DataParser
from pydispatch import dispatcher
import EventSignals
import math


class WorldData(object):
    __instance = None

    def __init__(self):
        self.dataParser = DataParser.getInstance()
        self.dataParser.LoadDataFile("inputData.xml")

        self.plants = []
        self.grazers = []
        self.predators = []
        self.obstacles = []

        dispatcher.connect(self.HandlePlantDeath, signal=EventSignals.plantDeath, sender=dispatcher.Any)
        dispatcher.connect(self.HandlePlantCreation, signal=EventSignals.plantCreation, sender=dispatcher.Any)
        dispatcher.connect(self.HandlePredatorDeath, signal=EventSignals.predatorDeath, sender=dispatcher.Any)
        dispatcher.connect(self.HandlePredatorCreation, signal=EventSignals.predatorCreation, sender=dispatcher.Any)
        dispatcher.connect(self.HandlePredatorSensing, signal=EventSignals.predatorSensing, sender=dispatcher.Any)
        dispatcher.connect(self.HandleOrganismDeath, signal=EventSignals.organismDeath, sender=dispatcher.Any)
        dispatcher.connect(self.HandleGrazerCreation, signal=EventSignals.grazerCreation, sender=dispatcher.Any)
        dispatcher.connect(self.HandleGrazerSensing, signal=EventSignals.grazerSensing, sender=dispatcher.Any)
        dispatcher.connect(self.HandleGrazerDeath, signal=EventSignals.grazerDeath, sender=dispatcher.Any)

    @classmethod
    def getInstance(wd):
        if not wd.__instance:
            wd.__instance = WorldData()
            print("Creating Instance...\n", WorldData.__instance)
        return wd.__instance

    def InitWorldData(self):
        # TODO: Attach appropriate graphics to each organism / obstacle
        self.currPlantNum = 0
        for plant in self.dataParser.InitialPlantList:
            self.plants.append(
                {
                    'ID': "PL" + str(self.currPlantNum).zfill(4),
                    'plant': plant
                    # 'img': 'plant.png'
                }
            )
            plant.SetId("PL" + str(self.currPlantNum).zfill(4))
            self.currPlantNum += 1

        self.currGrazerNum = 0
        for grazer in self.dataParser.InitialGrazerList:
            self.grazers.append(
                {
                    'ID': "GZ" + str(self.currGrazerNum).zfill(4),
                    'grazer': grazer
                    # 'img': 'grazer.png'
                }
            )
            grazer.SetId("GZ" + str(self.currGrazerNum).zfill(4))
            self.currGrazerNum += 1

        self.currPredatorNum = 0
        for predator in self.dataParser.InitialPredatorList:
            self.predators.append(
                {
                    'ID': "PR" + str(self.currPredatorNum).zfill(4),
                    'predator': predator
                    # 'img': 'predator.png'
                }
            )
            predator.SetId("PR" + str(self.currPredatorNum).zfill(4))
            self.currPredatorNum += 1

        self.currObstacleNum = 0
        for obstacle in self.dataParser.InitialObstacleList:
            self.obstacles.append(
                {
                    'ID': "OB" + str(self.currObstacleNum).zfill(4),
                    'obstacle': obstacle
                    # 'img': 'obstacle.png'
                }
            )
            self.currObstacleNum += 1

        # for plant in self.plants:
        #     #print(plant)
        # #print("\n\n")
        # for grazer in self.grazers:
        #     #print(grazer)
        # #print("\n\n")
        # for predator in self.predators:
        #     #print(predator)
        # #print("\n\n")
        # for obstacle in self.obstacles:
        #     #print(obstacle)
        # #print("\n\n")

    def Update(self):
        # print("Updating World Data...")
        for plant in self.plants:
            plant['plant'].PerformNextAction()
        for predator in self.predators:
            predator['predator'].PerformNextAction()
        for grazer in self.grazers:
            grazer['grazer'].PerformNextAction()

    def ResetWorld(self):
        print("Resetting World...")
        del self.plants[:]
        del self.grazers[:]
        del self.predators[:]
        del self.obstacles[:]
        self.dataParser.LoadDataFile("inputData.xml")
        self.InitWorldData()

    def HandlePlantDeath(self, sender):
        for plant in self.plants:
            if(plant['plant'].Id == sender):
                self.plants.remove(plant)
                # print("Plant ", sender, " was removed")

    def HandlePlantCreation(self, newPlant):
        self.plants.append(
            {
                'ID': "PL" + str(self.currPlantNum).zfill(4),
                'plant': newPlant
                # 'img': 'plant.png'
            }
        )
        newPlant.SetId("PL" + str(self.currPlantNum).zfill(4))
        self.currPlantNum += 1
        # print("New Plant Created! ID: ", newPlant.Id)

    def HandlePredatorDeath(self, sender):
        for predator in self.predators:
            if(predator['predator'].Id == sender):
                self.predators.remove(predator)
                # print("Predator: ", sender, " was removed")

    def HandlePredatorCreation(self, parent1, parent2, newPredator):
        self.predators.append(
            {
                'ID': "PR" + str(self.currPredatorNum).zfill(4),
                'predator': newPredator
                # 'img': 'predator.png'
            }
        )
        newPredator.SetId("PR" + str(self.currPredatorNum).zfill(4))
        newPredator.SetGenotype(parent1, parent2)
        newPredator.SetParents(parent1, parent2)
        self.currPredatorNum += 1
        # print("New Preadtor Created! ID: ", newPredator.Id)

    def HandlePredatorSensing(self, sender):
        for grazer in self.grazers:
            if math.hypot(sender.X - grazer['grazer'].X, sender.Y - grazer['grazer'].Y) <= 150:
                if grazer['grazer'] not in sender.grazersNearby:
                    sender.grazersNearby.append(grazer['grazer'])
        for predator in self.predators:
            if math.hypot(sender.X - predator['predator'].X, sender.Y - predator['predator'].Y) <= 150:
                if predator['predator'] not in sender.predatorsNearby:
                    sender.predatorsNearby.append(predator['predator'])

        for obstacle in self.obstacles:
            if math.hypot(sender.X - obstacle['obstacle'].X, sender.Y - obstacle['obstacle'].Y) <= 150:
                if obstacle['obstacle'] not in sender.obstaclesNearby:
                    sender.obstaclesNearby.append(obstacle['obstacle'])

        for predator in sender.predatorsNearby:
            if(predator == sender):
                sender.predatorsNearby.remove(predator)

    def HandleGrazerCreation(self, sender, newGrazer):
        self.grazers.append(
            {
                'ID': "GZ" + str(self.currGrazerNum).zfill(4),
                'grazer': newGrazer
            }
        )
        newGrazer.SetId("GZ" + str(self.currGrazerNum).zfill(4))
        self.currGrazerNum += 1
        # print("New Grazer Created! ID: ", newGrazer.Id)

    def HandleGrazerSensing(self, sender):
        for predator in self.predators:
            if math.hypot(sender.X - predator['predator'].X, sender.Y - predator['predator'].Y) <= 25:
                if predator['predator'] not in sender.predatorsNearby:
                    sender.predatorsNearby.append(predator['predator'])

        for plant in self.plants:
            if math.hypot(sender.X - plant['plant'].X, sender.Y - plant['plant'].Y) <= 150:
                if plant['plant'] not in sender.plantsNearby:
                    sender.plantsNearby.append(plant['plant'])

        for obstacle in self.obstacles:
            if math.hypot(sender.X - obstacle['obstacle'].X, sender.Y - obstacle['obstacle'].Y) <= 150:
                if obstacle['obstacle'] not in sender.obstaclesNearby:
                    sender.obstaclesNearby.append(obstacle['obstacle'])

    def HandleGrazerDeath(self, sender):
        for grazer in self.grazers:
            if(grazer['grazer'].Id == sender):
                self.grazers.remove(grazer)

    def HandleOrganismDeath(self, sender):
        for predator in self.predators:
            if(predator['predator'] == sender):
                self.predators.remove(predator)
                # print("Predator: ", sender, " was removed")
        for grazer in self.grazers:
            if(grazer['grazer'] == sender):
                self.grazers.remove(grazer)
                # print("Grazer: ", sender, " was removed")
