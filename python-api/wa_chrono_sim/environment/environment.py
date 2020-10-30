# ----------------------------------------------------------------------------------------
# 
# The environment class is supposed to be used for creating assets and placing them in 
# the Chrono scene. Assets include boxes or other visual components necessary for 
# visualizing the scene either in real time (irrlicht) or with sensors.
#
# ----------------------------------------------------------------------------------------

class WAEnvironment:
    def __init__(self):
        pass

    @staticmethod
    def CreateFromJSON():
        """
        Custom method for generating an environment from a JSON specification file
        """
        pass

    def Synchronize(self, time):
        """
        Synchronize environment to the current time (may only be necessary for dynamic environments)
        """
        pass

    def Advance(self, step):
        """  
        Advance environment computations one timestep (may only be necessary for dynamic environments)
        """
        pass