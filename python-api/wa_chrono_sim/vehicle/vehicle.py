# ----------------------------------------------------------------------------------------
# The vehicle class should be a lightweight wrapper for the Chrono vehicle module.
# The purpose of this class is to "hide" the intricacies of the ChVehicle, while
# also providing the ability to be a typical ChVehicle.
#
#
# A WAVehicle will hold a ChVehicle (in our case, a ChWheeledVehicle) and be relatively 
# similar to the Vehicle Models in the Chrono repo. It will allow JSON loading of custom
# model files and store important variables. 
#
# A WAVehicle is not necessarily responsible for a ChSystem, so a variable will be stored
# and a check will be done to see if it's necessary to step it.
#
# Another important feature of this class is the State representation. A WAVehicleState
# object is a component important for providing inputs to controllers.
#
# In the future, a ROS wrapper will be added to pass state information as needed.
#
# ----------------------------------------------------------------------------------------

import pychrono as chrono

class WAVehicle:
    def __init__(self, step_size, initLoc=chrono.ChVectorD(0,0,0.5), initRot=chrono.ChQuaternionD(1,0,0,0), visualize=True):
        pass

    @staticmethod
    def Create(vehicle):
        """
        Create a vehicle by passing in an already made ChWheeledVehicle object
        """
        pass

    @staticmethod
    def CreateFromJSON(filename, step_size, sys=None, contact_method=None, initLoc=chrono.ChVectorD(0,0,0.5), initRot=chrono.ChQuaternionD(1,0,0,0)):
        """
        Create a vehicle object from a json specification file.
        Chrono already provides this logic, this class just helps us create this class from a file.
        """
        pass

    def Synchronize(self, time):
        """
        Synchronize vehicle to the current time
        """
        pass

    def Advance(self, step):
        """  
        Advance vehicle one timestep
        """
        pass

    class WAVehicleState:
        """ Vehicle state class """

        def __init__(self, pos=chrono.ChVectorD(0,0,0), rot=chrono.ChQuaternionD(1,0,0,0), pos_dt=chrono.ChVectorD(0,0,0), rot_dt=chrono.ChQuaternionD(1,0,0,0)):
            """ Initialize a state object """
            pass
    
    def GetState(self):
        """ Return the vehicle state for passing between modules """
        pass