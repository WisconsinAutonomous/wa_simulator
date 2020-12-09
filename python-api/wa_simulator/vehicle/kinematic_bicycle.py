# WA Simulator
from wa_simulator.vehicle.vehicle import WAVehicle

# Other imports
import numpy as np

# ---------------------------
# WA Linear Kinematic Bicycle
# ---------------------------
class WALinearKinematicBicycle(WAVehicle):
    # Global filenames for vehicle models
    GO_KART_MODEL_FILE = 'vehicles/GoKart/GoKart_KinematicBicycle.json'
    IAC_VEH_MODEL_FILE = 'vehicles/IAC/IAC_KinematicBicycle.json'

    def __init__(self, 
                    filename : str, 
                    x=0,y=0,yaw=0,v=0):
        self.x = x
        self.y = y
        self.yaw = yaw
        self.v = v

        self.steering = 0
        self.throttle = 0
        self.braking = 0

        self.min_steering = -1.0
        self.max_steering = 1.0
        self.min_throttle = 0.0
        self.max_throttle = 1.0
        self.min_braking = 0.0
        self.max_braking = 1.0

    def Synchronize(self, time, driver_inputs : dict):
        if isinstance(driver_inputs, dict):
            s = driver_inputs["steering"]
            t = driver_inputs["throttle"]
            b = driver_inputs["braking"]
        else:
            raise TypeError('Synchronize: Type for driver inputs not recognized.')

        self.steering = np.clip(s, self.min_steering, self.max_steering)
        self.throttle = np.clip(t, self.min_throttle, self.max_throttle)
        self.braking = np.clip(b, self.min_braking, self.max_braking)

        if self.braking > 0:
            self.throttle = -self.braking

    def Advance(self, step):
        self.x += self.v * np.cos(self.yaw) * step
        self.y += self.v * np.sin(self.yaw) * step
        self.yaw += self.v / 3.776 * np.tan(self.steering) * step
        self.v += self.throttle * step
    
    def GetSimpleState(self):
        return self.x, self.y, self.yaw, self.v