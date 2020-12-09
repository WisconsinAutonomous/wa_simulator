# WA Simulator
from wa_simulator.vehicle.vehicle import WAVehicle, LoadVisualizationProperties
from wa_simulator.utilities.data_loader import GetWADataFile
from wa_simulator.utilities.constants import *

# Other imports
import numpy as np

def LoadVehicleProperties(filename):
    import json

    full_filename = GetWADataFile(filename)

    with open(full_filename) as f:
        j = json.load(f)
        
    if 'Visualization Properties' not in j:
        raise ValueError('Visualization Proprties not found in json.')
    
    return j['Vehicle Properties']

# ---------------------------
# WA Linear Kinematic Bicycle
# ---------------------------
class WALinearKinematicBicycle(WAVehicle):
    # Global filenames for vehicle models
    GO_KART_MODEL_FILE = 'vehicles/GoKart/GoKart_KinematicBicycle.json'
    IAC_VEH_MODEL_FILE = 'vehicles/IAC/IAC_KinematicBicycle.json'

    def __init__(self, filename, x=0, y=0, yaw=0, v=0):
        super().__init__(filename)

        # Simple state variables
        self.x = x
        self.y = y
        self.yaw = yaw
        self.v = v
        self.acc = 0

        # Wheel angular velocity
        self.omega = 0
        self.omega_dot = 0

        self.Initialize(LoadVehicleProperties(filename))

    def Initialize(self, vp):
        # Initialize vehicle properties
        self.mass = vp['Mass']

        # Torque coefficients
        self.a = vp['Torque Coefficients']

        # Gear ratio, effective radius and inertia
        self.GR = vp['Gear Ratio']
        self.r_eff = vp['Effective Radius']
        self.J_e = vp['Inertia']

        # Aerodynamic and friction coefficients
        self.c_a = vp['Aerodynamic Coefficient']
        self.c_rl = vp['Friction Coefficient']

        # Tire forces
        self.c = vp['C']
        self.F_max = vp['Max Force']

        # Save vehicle inputs
        self.steering = 0
        self.throttle = 0
        self.braking = 0

        self.L = vp['Wheelbase']
        (self.min_steering, self.max_steering) = vp['Steering']
        (self.min_throttle, self.max_throttle) = vp['Throttle']
        (self.min_braking, self.max_braking) = vp['Braking']

    def Synchronize(self, time, driver_inputs : dict):
        if isinstance(driver_inputs, dict):
            s = driver_inputs['steering']
            t = driver_inputs['throttle']
            b = driver_inputs['braking']
        else:
            raise TypeError('Synchronize: Type for driver inputs not recognized.')

        self.steering = np.clip(s, self.min_steering, self.max_steering)
        self.throttle = np.clip(t, self.min_throttle, self.max_throttle)
        self.braking = np.clip(b, self.min_braking, self.max_braking)

        if self.braking > 1e-1:
            self.throttle = -self.braking

    def Advance(self, step):
        if self.v == 0 and self.throttle == 0:
            F_x = 0
            F_load = 0
            T_e = 0
        else:
            if self.v == 0:
                # Remove possibity of divide by zero error
                self.v = 1e-8
                self.omega = 1e-8

            # Update engine and tire forces
            F_aero = self.c_a * self.v ** 2
            R_x = self.c_rl * self.v
            F_g = self.mass * GRAVITY * np.sin(0)
            F_load = F_aero + R_x + F_g
            T_e = self.throttle * (self.a[0] + self.a[1] * self.omega + self.a[2] * self.omega ** 2)
            omega_w = self.GR * self.omega  # Wheel angular velocity
            s = (omega_w * self.r_eff - self.v) / self.v # slip ratio
            cs = self.c * s

            if abs(s) < 1:
                F_x = cs
            else:
                F_x = self.F_max
        
        if self.throttle < 0:
            if self.v <= 0:
                F_x = 0
            else:
                F_x = -abs(F_x)

        # Update state information
        self.x += self.v * np.cos(self.yaw) * step
        self.y += self.v * np.sin(self.yaw) * step
        self.yaw += self.v / self.L * np.tan(self.steering) * step
        self.v += self.acc * step
        self.acc = (F_x - F_load) / self.mass
        self.omega += self.omega_dot * step
        self.omega_dot = (T_e - self.GR * self.r_eff * F_load) / self.J_e
    
    def GetSimpleState(self):
        return self.x, self.y, self.yaw, self.v