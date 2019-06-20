# We need to make our report in csv format
# this makes it easily importable into Excel

import csv
import datetime


class Report():
    # Main goal of this is just to output the data
    # Assumes data comes in a struct

    def create(self, dataDump, timeStamp):

        # Begin by opening the file
        # We will use the simTime in seconds and divide it out to get hrs, min, sec
        timeHrMnSc = str(datetime.timedelta(seconds=timeStamp))

        # replace the default ':' with '_'
        timeHrMnSc = timeHrMnSc.replace(':', '_')

        # Create filename based on the timestep
        filename = 'SimReport_' + timeHrMnSc + '.csv'

        # open the file with our new filename in write mode
        with open(filename, 'w') as csvfile:

            # Set up the csv file writing format, this one is pretty standard
            filewrite = csv.writer(
                csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

            # This writes out the headers for each field requested by the professor
            filewrite.writerow(['ID', 'OrganismType', 'X-Position',
                                'Y-Position', 'Energy Level', 'LifeStage', 'Genes'])

            # Now we loop through each key in the dictionary and populate our rows
            for data in dataDump:
                # The keys in the dictionary are the organism ID
                id = data['ID']

                # Initialize the organismType
                organismType = ''
                organismKey = ''
                xPosition = ''
                yPosition = ''

                # Plants & Obstacles only have diameter not energy
                energyLevel = 'NA'

                # Not all organisms have a defined maturityLevel, initialized to 'NA'
                maturityLevel = 'NA'

                # Not all organisms have determinable genes, initialized to 'NA'
                genes = 'NA'

                # The IDs contain a 2 letter prefix that tells the organism type,
                # the prefix for plants is PL
                if id[:2] == 'PL':
                    organismType = 'plant'
                    maturityLevel = data[organismType].LifeStage.name

                # the prefix for grazers is GZ
                elif id[:2] == 'GZ':
                    organismType = 'grazer'
                    energyLevel = data[organismType].EnergyLevel

                # the prefix for predators is PR
                elif id[:2] == 'PR':
                    organismType = 'predator'
                    energyLevel = data[organismType].EnergyLevel
                    maturityLevel = data[organismType].LifeStage.name
                    genes = data[organismType].Genotype

                # if it is not one of the organisms listed above it is an obstacle
                else:
                    organismType = 'obstacle'

                xPosition = data[organismType].X
                yPosition = data[organismType].Y

                filewrite.writerow(
                    [id, organismType, xPosition, yPosition, energyLevel, maturityLevel, genes])
