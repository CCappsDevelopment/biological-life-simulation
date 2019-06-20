import xml.etree.ElementTree as ElementTree
from Obstacle import Obstacle
from Plant import Plant
from Predator import Predator
from Grazer import Grazer
import re


class DataParser:
    __instance = None

    def __init__(self):
        # world
        self.WorldWidth = 0.0
        self.WorldHeight = 0.0

        # plants
        self.InitialPlantList = None
        self.InitialPlantCount = 0
        self.PlantGrowthRate = 0.0
        self.MaxPlantSize = 0
        self.MaxSeedCastDistance = 0
        self.MaxSeedNumber = 0
        self.SeedViabilityPercentage = 0.0

        # grazers
        self.InitialGrazerList = None
        self.InitialGrazerCount = 0
        self.GrazerEnergyInputRate = 0  # Energy input per minute while grazing
        self.GrazerEnergyOutputRate = 0  # Energy output when moving each 5 DU
        self.GrazerEnergyToReproduce = 0  # Energy required to reproduce
        # How long (in minutes) that the grazer can maintain max speed
        self.GrazerMaxSpeedTime = 0.0
        self.GrazerMaxSpeed = 0.0

        # predators
        self.InitialPredatorList = None
        self.InitialPredatorCount = 0
        # Max speed for Homozygous Dominant (FF)
        self.PredatorMaxSpeedHOD = 0.0
        # Max speed for Heterozygous Dominant (Ff)
        self.PredatorMaxSpeedHED = 0.0
        # Max speed for Homozygous Recessive (ff)
        self.PredatorMaxSpeedHOR = 0.0
        self.PredatorEnergyOutputRate = 0  # Energy output when moving each 5 DU
        self.PredatorEnergyToReproduce = 0  # Energy level needed to reproduce
        # How long (in minutes) that the predator can maintain max speed
        self.PredatorMaxSpeedTime = 0.0
        self.PredatorMaxOffspring = 0  # Maximum number of offspring when reproducing
        self.PredatorGestationPeriodDays = 0.0  # Gestation period to reproduce in days
        self.PredatorOffspringEnergyLevel = 0  # The energy level of offspring at birth

        # obstacles
        self.InitialObstacleList = None
        self.InitialObstacleCount = 0

    @classmethod
    def getInstance(dp):
        if not dp.__instance:
            dp.__instance = DataParser()
            print("Creating DataParser Instance...\n", DataParser.__instance)
        return dp.__instance

    def LoadDataFile(self, fileName):
        tree = ElementTree.parse(open(fileName))
        root = tree.getroot()

        # World Map Constants
        worldMap = root.find("./LAND_BOUNDS")
        self.WorldWidth = float(worldMap.find("WIDTH").text)
        self.WorldHeight = float(worldMap.find("HEIGHT").text)

        # Plants
        plants = root.find("./PLANTS")
        self.InitialPlantCount = int(plants.find("INITIAL_PLANT_COUNT").text)
        self.PlantGrowthRate = float(plants.find("GROWTH_RATE").text)
        self.MaxPlantSize = int(plants.find("MAX_SIZE").text)
        self.MaxSeedCastDistance = int(
            plants.find("MAX_SEED_CAST_DISTANCE").text)
        self.MaxSeedNumber = int(plants.find("MAX_SEED_NUMBER").text)
        self.SeedViabilityPercentage = float(
            plants.find("SEED_VIABILITY").text)
        self.InitialPlantList = []

        for plant in plants.findall("PLANT"):
            self.InitialPlantList.append(
                Plant(
                    int(plant.find("X_POS").text),
                    int(plant.find("Y_POS").text),
                    int(plant.find("P_DIAMETER").text)
                )
            )

        # Grazers
        grazers = root.find("./GRAZERS")
        self.InitialGrazerCount = int(
            grazers.find("INITIAL_GRAZER_COUNT").text)
        self.GrazerEnergyInputRate = int(grazers.find("G_ENERGY_INPUT").text)
        self.GrazerEnergyOutputRate = int(grazers.find("G_ENERGY_OUTPUT").text)
        self.GrazerEnergyToReproduce = int(
            grazers.find("G_ENERGY_TO_REPRODUCE").text)
        self.GrazerMaxSpeedTime = float(grazers.find("G_MAINTAIN_SPEED").text)
        self.GrazerMaxSpeed = float(grazers.find("G_MAX_SPEED").text)
        self.InitialGrazerList = []

        for grazer in grazers.findall("GRAZER"):
            self.InitialGrazerList.append(
                Grazer(
                    int(grazer.find("X_POS").text),
                    int(grazer.find("Y_POS").text),
                    int(grazer.find("G_ENERGY_LEVEL").text)
                )
            )

        # Predators
        predators = root.find("./PREDATORS")
        self.InitialPredatorCount = int(
            predators.find("INITIAL_PREDATOR_COUNT").text)
        self.PredatorMaxSpeedHOD = float(predators.find("MAX_SPEED_HOD").text)
        self.PredatorMaxSpeedHED = float(predators.find("MAX_SPEED_HED").text)
        self.PredatorMaxSpeedHOR = float(predators.find("MAX_SPEED_HOR").text)
        self.PredatorMaxSpeedTime = float(
            predators.find("P_MAINTAIN_SPEED").text)
        self.PredatorEnergyOutputRate = int(
            predators.find("P_ENERGY_OUTPUT").text)
        self.PredatorEnergyToReproduce = int(
            predators.find("P_ENERGY_TO_REPRODUCE").text)
        self.PredatorMaxOffspring = int(predators.find("P_MAX_OFFSPRING").text)
        self.PredatorGestationPeriodDays = float(
            predators.find("P_GESTATION").text)
        self.PredatorOffspringEnergyLevel = int(
            predators.find("P_OFFSPRING_ENERGY").text)
        self.InitialPredatorList = []

        prID = 0

        for predator in predators.findall("PREDATOR"):
            genotype = predator.find("GENOTYPE").text
            genotype = re.sub(r"[\n\t]*", "", genotype).split()
            self.InitialPredatorList.append(
                Predator(
                    int(predator.find("X_POS").text),
                    int(predator.find("Y_POS").text),
                    int(predator.find("P_ENERGY_LEVEL").text),
                    genotype,
                    prID
                )
            )
            prID += 1

        # Obstacles
        obstacles = root.find("./OBSTACLES")
        self.InitialObstacleCount = int(
            obstacles.find("INITIAL_OBSTACLE_COUNT").text)
        self.InitialObstacleList = []

        for obstacle in obstacles.findall("OBSTACLE"):
            self.InitialObstacleList.append(
                Obstacle(
                    int(obstacle.find("X_POS").text),
                    int(obstacle.find("Y_POS").text),
                    int(obstacle.find("O_DIAMETER").text),
                    int(obstacle.find("O_HEIGHT").text)
                )
            )
