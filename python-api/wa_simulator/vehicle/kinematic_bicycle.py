"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# WA Simulator
from .vehicle import WAVehicle, LoadPropertiesFromJSON
from ..utilities.data_loader import GetWADataFile
from ..utilities.constants import *

# Other imports
import numpy as np


class WALinearKinematicBicycle(WAVehicle):
    """A linear, kinematic bicycle model

    Args:
        filename (str): json specification file used to describe the parameters for the vehicle
        x (double, optional): x position of the vehicle. Defaults to 0.
        y (double, optional): y position of the vehicle. Defaults to 0.
        yaw (double, optional): angle about the Z. Defaults to 0.
        v (double, optional): speed of the vehicle. Defaults to 0.

    Attributes:
        GO_KART_MODEL_FILE (str): evGrand Prix json file that describes an vehicle for that comp.
        IAC_VEH_MODEL_FILE (str): Indy Autonomous Challange json file that describes an vehicle for that comp.
        x (double): x position of the vehicle
        y (double): y position of the vehicle
        yaw (double): angle about the Z
        v (double): speed of the vehicle
        omega (double): wheel angular velocity
        omega_dot (double): wheel angular acceleration
        mass (double): vehicle mass
        a (list): 2nd order torque coefficients
        GR (double): gear ratio
        r_eff (double): Effective radius at which the vehicle can turn
        J_e (double): Inertia of the vehicle
        c_a (double): Aerodynamic coefficient
        c_rl (double): Friction coefficient
        c (double): Tire force
        F_max (double): Max force imposed at the wheel
        L (double): Vehicle wheelbase (distance between front and back axles)
        min_steering (double): Minimum steering value allowed
        max_steering (double): Maximum steering value allowed
        min_throttle (double): Minimum throttle value allowed
        max_throttle (double): Maximum throttle value allowed
        min_braking (double): Minimum braking value allowed
        max_braking (double): Maximum braking value allowed
    """

    # Global filenames for vehicle models
    GO_KART_MODEL_FILE = "vehicles/GoKart/GoKart_KinematicBicycle.json"
    IAC_VEH_MODEL_FILE = "vehicles/IAC/IAC_KinematicBicycle.json"

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

        self.Initialize(LoadPropertiesFromJSON(filename, "Vehicle Properties"))

    def Initialize(self, vp):
        # Initialize vehicle properties
        self.mass = vp["Mass"]

        # Torque coefficients
        self.a = vp["Torque Coefficients"]

        # Gear ratio, effective radius and inertia
        self.GR = vp["Gear Ratio"]
        self.r_eff = vp["Effective Radius"]
        self.J_e = vp["Inertia"]

        # Aerodynamic and friction coefficients
        self.c_a = vp["Aerodynamic Coefficient"]
        self.c_rl = vp["Friction Coefficient"]

        # Tire forces
        self.c = vp["C"]
        self.F_max = vp["Max Force"]

        self.L = vp["Wheelbase"]
        (self.min_steering, self.max_steering) = vp["Steering"]
        (self.min_throttle, self.max_throttle) = vp["Throttle"]
        (self.min_braking, self.max_braking) = vp["Braking"]

    def Synchronize(self, time, vehicle_inputs):
        """Synchronize the vehicle inputs to the values in this model

        Args:
            time (double): time at which to update the vehicle to
            vehicle_inputs (WAVehicleInputs): vehicle inputs
        """
        s = vehicle_inputs.steering
        t = vehicle_inputs.throttle
        b = vehicle_inputs.braking

        self.steering = np.clip(s, self.min_steering, self.max_steering)
        self.throttle = np.clip(t, self.min_throttle, self.max_throttle)
        self.braking = np.clip(b, self.min_braking, self.max_braking)

        if self.braking > 1e-1:
            self.throttle = -self.braking

    def Advance(self, step):
        """Perform a dynamics update

        Args:
            step (double): time step to update the vehicle by
        """
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
            T_e = self.throttle * (
                self.a[0] + self.a[1] * self.omega + self.a[2] * self.omega ** 2
            )
            omega_w = self.GR * self.omega  # Wheel angular velocity
            s = (omega_w * self.r_eff - self.v) / self.v  # slip ratio
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
        """Get a simple state representation of the vehicle.

        Returns:
            tuple: (x position, y position, yaw about the Z, speed)
        """
        return self.x, self.y, self.yaw, self.v