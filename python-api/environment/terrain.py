# ----------------------------------------------------------------------------------------
# 
# The terrain class is a helper class for wrapping a ChTerrain (in our case, a 
# RigidTerrain). Basically provides helper functions and JSON loading capabilities
#
# ----------------------------------------------------------------------------------------

class WATerrain:
    def __init__(self):
        pass

    @staticmethod
    def CreateFromJSON():
        """
        Create a RigidTerrain from a json specification file
        """
        pass

    def Synchronize(self, time):
        """
        Synchronize terrain to the current time (not really necessary for a RigidTerrain)
        """
        pass

    def Advance(self, step):
        """  
        Advance terrain computations one timestep (not really necessary for a RigidTerrain)
        """
        pass