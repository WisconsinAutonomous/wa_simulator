"""
Wisconsin Autonomous - https://wa.wisc.edu

Copyright (c) 2021 wa.wisc.edu
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

from abc import abstractmethod  # Abstract Base Class

# WA Simulator
from wa_simulator.core import WA_GRAVITY, WAVector, WAQuaternion
from wa_simulator.base import WABase
from wa_simulator.utils import _load_json, _WAStaticAttribute, get_wa_data_file

# Other imports
import numpy as np


def load_properties_from_json(filename: str, prop: str) -> dict:
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
    j = _load_json(filename)

    if prop not in j:
        raise ValueError(f"{prop} not found in json.")

    return j[prop]


class WAVehicle(WABase):
    """Base class for a WAVehicle.

    To implement a new vehicle model, override this class. A WAVehicle should interact
    with the terrain/assets/world and take three inputs: steering, throttle, braking.

    Args:
        system (WASystem): the system used to run the simulation
        vehicle_inputs (WAVehicleInputs): The vehicle inputs
        filename (str, optional): Filename to be used for visualization properties
    """

    def __init__(self, system: 'WASystem', vehicle_inputs: 'WAVehicleInputs', filename=None):
        self._system = system
        self._vehicle_inputs = vehicle_inputs

        self._vis_properties = (
            dict()
            if filename is None
            else load_properties_from_json(filename, "Visualization Properties")
        )

    def get_visual_properties(self) -> dict:
        """Get visual properties for visualizing the vehicle

        .. todo::
            Define the visual properties required

        Returns:
            dict: the visual properties
        """
        return self._vis_properties

    @abstractmethod
    def synchronize(self, time: float):
        pass

    @abstractmethod
    def advance(self, step: float):
        pass

    def is_ok(self) -> bool:
        return True

    @abstractmethod
    def get_pos(self) -> WAVector:
        """Get the center of mass (COM) position of the vehicle.

        Returns:
            WAVector: the position of the vehicle
        """
        pass

    @abstractmethod
    def get_rot(self) -> WAQuaternion:
        """Get the rotation about the center of mass (COM) of the vehicle

        Returns:
            WAQuaternion: the vehicles orientation
        """
        pass

    @abstractmethod
    def get_pos_dt(self) -> WAVector:
        """Get the instantaneous velocity of the vehicle

        Returns:
            WAVector: The velocity where X is forward, Z is up and Y is left (ISO standard)
        """
        pass

    @abstractmethod
    def get_rot_dt(self) -> WAQuaternion:
        """Get the angular velocity of the vehicle

        Returns:
            WAQuaternion: The angular velocity
        """
        pass

    @abstractmethod
    def get_pos_dtdt(self) -> WAVector:
        """Get the acceleration of the vehicle

        Returns:
            WAVector: The acceleration where X is forward, Z is up and Y is left (ISO standard)
        """
        pass

    @abstractmethod
    def get_rot_dtdt(self) -> WAQuaternion:
        """Get the angular acceleration of the vehicle

        Returns:
            WAQuaternion: The angular acceleration
        """
        pass


class WALinearKinematicBicycle(WAVehicle):
    """A linear, kinematic bicycle model

    Args:
        system (WASystem): the system used to run the simulation
        vehicle_inputs (WAVehicleInputs): The vehicle inputs
        filename (str): json specification file used to describe the parameters for the vehicle
        init_pos (WAVector): initial position
        init_rot (WAQuaternion): initial rotation
        init_pos_dt (WAVector): initial velocity
    """

    # Global filenames for vehicle models
    _GO_KART_MODEL_FILE = "vehicles/GoKart/GoKart_KinematicBicycle.json"

    GO_KART_MODEL_FILE = _WAStaticAttribute('_GO_KART_MODEL_FILE', get_wa_data_file)

    def __init__(self, system: 'WASystem', vehicle_inputs: 'WAVehicleInputs', filename: str, init_pos: WAVector = WAVector(), init_rot: WAQuaternion = WAQuaternion.from_z_rotation(0), init_pos_dt: WAVector = WAVector()):
        super().__init__(system, vehicle_inputs, filename)

        # Simple state variables
        self._x = init_pos.x
        self._y = init_pos.y
        self._yaw = init_rot.to_euler_yaw()
        self._v = init_pos_dt.length
        self._acc = 0.0

        self._steering = 0
        self._throttle = 0
        self._braking = 0

        # Wheel angular velocity
        self._omega = 0.0
        self._omega_dot = 0.0

        self._yaw_dt = 0.0
        self._yaw_dtdt = 0.0
        self._last_yaw = 0.0

        properties = load_properties_from_json(filename, "Vehicle Properties")
        self._initialize(properties)

    def _initialize(self, vp):
        """Initialize the vehicle parameters

        Expected properties:
            "Wheelbase" (float): distance between the front and back tire
            "Mass" (float): mass of the vehicle
            "Gear Ratio" (float): gear ratio of the simulated powertrain
            "Effective Radius" (float): 
            "Inertia" (float): Effective inertia for the vehicle
            "Aerodynamic Coefficient" (float):
            "Friction Coefficient" (float):
            "C" (float)
            "Max Force" (float)
            "Torque Coefficients" (list)
            "Steering" ([min, max]): Min and max throttle values
            "Throttle" ([min, max]): Min and max throttle values
            "Braking" ([min, max]): Min and max braking values

        Args:
            vp (dict): Vehicle preoperties (see above for expected keys)
        """

        # Initialize vehicle properties
        self._mass = vp["Mass"]

        # Torque coefficients
        self._a = vp["Torque Coefficients"]

        # Gear ratio, effective radius and inertia
        self._GR = vp["Gear Ratio"]
        self._r_eff = vp["Effective Radius"]
        self._J_e = vp["Inertia"]

        # Aerodynamic and friction coefficients
        self._c_a = vp["Aerodynamic Coefficient"]
        self._c_rl = vp["Friction Coefficient"]

        # Tire forces
        self._c = vp["C"]
        self._F_max = vp["Max Force"]

        self._L = vp["Wheelbase"]
        (self._min_steering, self._max_steering) = vp["Steering"]
        (self._min_throttle, self._max_throttle) = vp["Throttle"]
        (self._min_braking, self._max_braking) = vp["Braking"]

    def synchronize(self, time):
        s = self._vehicle_inputs.steering
        t = self._vehicle_inputs.throttle
        b = self._vehicle_inputs.braking

        self._steering = np.clip(s, self._min_steering, self._max_steering)
        self._throttle = np.clip(t, self._min_throttle, self._max_throttle)
        self._braking = np.clip(b, self._min_braking, self._max_braking)

        if self._braking > 1e-1:
            self._throttle = -self._braking

    def advance(self, step):
        # TODO: COMMENT!
        if self._v == 0 and self._throttle == 0:
            F_x = 0
            F_load = 0
            T_e = 0
        else:
            if self._v == 0:
                # Remove possibity of divide by zero error
                self._v = 1e-8
                self._omega = 1e-8

            # Update engine and tire forces
            F_aero = self._c_a * self._v ** 2
            R_x = self._c_rl * self._v
            F_g = self._mass * WA_GRAVITY * np.sin(0)
            F_load = F_aero + R_x + F_g
            T_e = self._throttle * (
                self._a[0] + self._a[1] * self._omega +
                self._a[2] * self._omega ** 2
            )
            omega_w = self._GR * self._omega  # Wheel angular velocity
            s = (omega_w * self._r_eff - self._v) / self._v  # slip ratio
            cs = self._c * s

            if abs(s) < 1:
                F_x = cs
            else:
                F_x = self._F_max

        if self._throttle < 0:
            if self._v <= 0:
                F_x = 0
            else:
                F_x = -abs(F_x)

        # Update state information
        self._x += self._v * np.cos(self._yaw) * step
        self._y += self._v * np.sin(self._yaw) * step
        self._yaw += self._v / self._L * np.tan(self._steering) * step
        self._v += self._acc * step
        self._acc = (F_x - F_load) / self._mass
        self._omega += self._omega_dot * step
        self._omega_dot = (T_e - self._GR * self._r_eff * F_load) / self._J_e

        v_epsilon = abs(self._v) > 0.1
        self._yaw_dt = (self._last_yaw - self._yaw) / step if v_epsilon else 0
        self._yaw_dtdt = (self._last_yaw - self._yaw) / step if v_epsilon else 0  # noqa
        self._last_yaw = self._yaw

    def get_pos(self) -> WAVector:
        return WAVector([self._x, self._y, 0.0])

    def get_rot(self) -> WAQuaternion:
        return WAQuaternion.from_z_rotation(self._yaw)

    def get_pos_dt(self) -> WAVector:
        return WAVector([self._v * np.cos(self._yaw), self._v * np.sin(self._yaw), 0.0])

    def get_rot_dt(self) -> WAQuaternion:
        return WAQuaternion.from_z_rotation(self._yaw_dt)

    def get_pos_dtdt(self) -> WAVector:
        angle = np.tan(np.interp(self._steering, [-1, 1], [self._min_steering, self._max_steering]))  # noqa
        angle = angle if angle != 0 else 1e-3
        tr = self._L / angle
        tr = tr if tr != 0 else 1e-3
        return WAVector([self._acc, self._v ** 2 / tr, WA_GRAVITY])

    def get_rot_dtdt(self) -> WAQuaternion:
        return WAQuaternion.from_z_rotation(self._yaw_dtdt)
