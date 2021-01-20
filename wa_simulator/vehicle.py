"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

from abc import ABC, abstractmethod  # Abstract Base Class

# WA Simulator
from wa_simulator.data_loader import get_wa_data_file
from wa_simulator.constants import GRAVITY

# Other imports
import numpy as np


def load_properties_from_json(filename, prop):
    """Load a specified property from a json specification file

    Will load a json file and extract the passed property field for use
    by the underyling vehicle object

    Args:
        filename (str): the filename location within the set WA data folder for the json file
        property (str): the property to get. Ex: "Vehicle Properties"

    Raises:
        ValueError: The property field isn't found

    Returns:
        dict: the property field extracted from the json file
    """
    import json

    full_filename = get_wa_data_file(filename)

    with open(full_filename) as f:
        j = json.load(f)

    if prop not in j:
        raise ValueError(f"{prop} not found in json.")

    return j[prop]


class WAVehicle(ABC):
    """Base class for a WAVehicle.

    To implement a new vehicle model, override this class. A WAVehicle should interact
    with the terrain/assets/world and take three inputs: steering, throttle, braking.

    Args:
        filename (str, optional): Filename to be used for visualization properties

    Attributes:
        vis_properties (dict): Visual properties used for visualization of the vehicle.
    """

    def __init__(self, filename=None):
        self.vis_properties = (
            dict()
            if filename is None
            else load_properties_from_json(filename, "Visualization Properties")
        )

    @abstractmethod
    def synchronize(self, time, vehicle_inputs):
        """Synchronize the vehicle at the specified time and driver inputs

        Args:
            time (double): the time at which the synchronize the vehicle to
            vehicle_inputs (WAVehicleInputs): Inputs for the underyling dynamics
        """
        pass

    @abstractmethod
    def advance(self, step):
        """Advance the vehicle by the specified step

        Args:
            step (double): how much to advance the vehicle by
        """
        pass

    @abstractmethod
    def get_simple_state(self):
        """Get a simple state representation of the vehicle.

        Must return a tuple with the following values:
            (x position, y position, yaw about the Z, speed)
        """
        pass


class WALinearKinematicBicycle(WAVehicle):
    """A linear, kinematic bicycle model

    Args:
        filename (str): json specification file used to describe the parameters for the vehicle
        x (double, optional): x position of the vehicle. Defaults to 0.
        y (double, optional): y position of the vehicle. Defaults to 0.
        yaw (double, optional): angle about the Z. Defaults to 0.
        v (double, optional): speed of the vehicle. Defaults to 0.

    Attributes:
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

        self.initialize(load_properties_from_json(
            filename, "Vehicle Properties"))

    def initialize(self, vp):
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

    def synchronize(self, time, vehicle_inputs):
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

    def advance(self, step):
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
                self.a[0] + self.a[1] * self.omega +
                self.a[2] * self.omega ** 2
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

    def get_simple_state(self):
        """Get a simple state representation of the vehicle.

        Returns:
            tuple: (x position, y position, yaw about the Z, speed)
        """
        return self.x, self.y, self.yaw, self.v
