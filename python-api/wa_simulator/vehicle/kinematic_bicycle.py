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

    def Synchronize(self, time, driver_inputs : dict):
        if isinstance(driver_inputs, dict):
            s = driver_inputs["steering"]
            t = driver_inputs["throttle"]
            b = driver_inputs["braking"]
        else:
            raise TypeError('Synchronize: Type for driver inputs not recognized.')

        self.steering = np.clip(s, self.min_steering, self.max_steering)
        self.throttle = np.clip(s, self.min_throttle, self.max_throttle)
        self.braking = np.clip(s, self.min_braking, self.max_braking)

        if self.braking > 0:
            self.throttle = -self.braking

    def Advance(self, step):
        self.x += self.v * np.cos(self.yaw) * step
        self.y += self.v * np.sin(self.yaw) * step
        self.yaw += self.v / L * np.tan(self.steering) * step
        self.yaw = normalize_angle(self.yaw)
        self.v += self.throttle * step
    
    def GetSimpleState(self):
        return self.x, self.y, self.yaw, self.v

def normalize_angle(angle):
    """
    Normalize an angle to [-pi, pi].
    :param angle: (float)
    :return: (float) Angle in radian in [-pi, pi]
    """
    while angle > np.pi:
        angle -= 2.0 * np.pi

    while angle < -np.pi:
        angle += 2.0 * np.pi

    return angle