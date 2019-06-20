class Obstacle():
    # initialize the class and populate data
    # these do not spawn so they are pretty simple
    def __init__(self, X, Y, diameter, height):
        # set diameter
        self.Diameter = diameter
        # set height
        self.Height = height
        # finish initialization
        self.X = X
        self.Y = Y

    # don't have any actions but needed to stay still
    def PerformNextAction(self):
        self.X = self.X + 1
