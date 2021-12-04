"""
Wisconsin Autonomous - https://wa.wisc.edu

Copyright (c) 2021 wa.wisc.edu
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

from abc import ABC, abstractmethod  # Abstract Base Class

# WA Simulator
from wa_simulator.base import WABase
from wa_simulator.visualization import WAMatplotlibVisualization
from wa_simulator.utils import _check_type

# Other imports
import sys
import numpy as np


class WAController(WABase):
    """Base class for a controller

    Controllers are responsible for outputting a steering, throttle and braking value.
    This is done because in real life, those are the inputs our cars will have. The
    derived controller's (i.e. the new class that inherits from this class)
    responsibility is to take inputs from the simulation and return these values
    through the get_inputs method.

    Args:
        system (WASystem): The system used to manage the simulation
        vehicle_inputs (WAVehicleInputs): The vehicle inputs

    Attributes:
        steering (float): steering input.
        throttle (float): throttle input.
        braking (float): braking input.
    """

    def __init__(self, system: 'WASystem', vehicle_inputs: 'WAVehicleInputs'):
        self._system = system
        self._vehicle_inputs = vehicle_inputs

    @abstractmethod
    def synchronize(self, time: float):
        pass

    @abstractmethod
    def advance(self, step: float):
        pass

    def is_ok(self) -> bool:
        return True

    def get_inputs(self) -> 'WAVehicleInputs':
        """Get the vehicle inputs

        Returns:
            WAVehicleInputs: The input class
        """
        return self._vehicle_inputs

    def _get_steering(self) -> float:
        return self._vehicle_inputs.steering

    def _get_throttle(self) -> float:
        return self._vehicle_inputs.throttle

    def _get_braking(self) -> float:
        return self._vehicle_inputs.braking

    def _set_steering(self, steering: float):
        self._vehicle_inputs.steering = steering

    def _set_throttle(self, throttle: float):
        self._vehicle_inputs.throttle = throttle

    def _set_braking(self, braking: float):
        self._vehicle_inputs.braking = braking

    steering = property(_get_steering, _set_steering)
    throttle = property(_get_throttle, _set_throttle)
    braking = property(_get_braking, _set_braking)


class _WAKeyboardController(WAController):
    """Base keyboard controller. Still must be inherited (can't be instantiated). Has utilites.

    Args:
        system (WASystem): The system used to manage the simulation
        vehicle_inputs (WAVehicleInputs): The vehicle inputs
    """

    def __init__(self, system: 'WASystem', vehicle_inputs: 'WAVehicleInputs'):
        super().__init__(system, vehicle_inputs)

        self._steering_target = 0
        self._throttle_target = 0
        self._braking_target = 0

        self._steering_delta = system.render_step_size / 2.0
        self._throttle_delta = system.render_step_size / 6.0
        self._braking_delta = system.render_step_size / 1.5

        self._steering_gain = 4.0
        self._throttle_gain = 4.0
        self._braking_gain = 4.0

    def set_steering_delta(self, steering_delta: float):
        """Sets the steering delta value

        Args:
            steering_delta (float): the new steering delta value
        """
        self._steering_delta = steering_delta

    def set_throttle_delta(self, throttle_delta: float):
        """Sets the throttle delta value

        Args:
            throttle_delta (float): the new throttle delta value
        """
        self._throttle_delta = throttle_delta

    def set_braking_delta(self, braking_delta: float):
        """Sets the braking delta value

        Args:
            braking_delta (float): the new braking delta value
        """
        self._braking_delta = braking_delta

    def set_gains(self, steering_gain: float, throttle_gain: float, braking_gain: float):
        """Sets the controllers gains

        Args:
            steering_gain (float): the new steering gain
            throttle_gain (float): the new throttle gain
            braking_gain (float): the new braking gain
        """
        self._steering_gain = steering_gain
        self._throttle_gain = throttle_gain
        self._braking_gain = braking_gain

    def advance(self, step: float):
        """Advance the controller by the specified step

        Integrates dynamics over some step range. If the original step is the same as the passed
        step value, the method is only run once.

        Args:
                step (float): the time step at which the controller should be advanced
        """
        # Integrate dynamics, taking as many steps as required to reach the value 'step'
        t = 0
        while t < step:
            h = step - t

            steering_deriv = self._steering_gain * \
                (self._steering_target - self.steering)
            throttle_deriv = self._throttle_gain * \
                (self._throttle_target - self.throttle)
            braking_deriv = self._braking_gain * \
                (self._braking_target - self.braking)

            self.steering += min(self._steering_delta,
                                 h * steering_deriv, key=abs)
            self.throttle += min(self._throttle_delta,
                                 h * throttle_deriv, key=abs)
            self.braking += min(self._braking_delta, h *
                                braking_deriv, key=abs)

            t += h

    def _update(self, key: int):
        """Update the target values based on the key.

        The updated target values are based off the delta values for that respective input.
        In this controller, input values are clipped at [-1,1] or [0,1].

        0: throttle increase, braking decreases (up)
        1: adjust steering right (right)
        2: brake increase, throttle decrease (down)
        3: adjust steering left (left)

        Args:
            key (int): the key input
        """
        allowed_keys = [0, 1, 2, 3]

        # Mouse click
        if key == -1:
            return

        # Up
        if key == 0:
            self._throttle_target = np.clip(
                self._throttle_target + self._throttle_delta, 0.0, +1.0)
            if self._throttle_target > 0:
                self._braking_target = np.clip(
                    self._braking_target - self._braking_delta * 3, 0.0, +1.0)
        # Down
        elif key == 2:
            self._throttle_target = np.clip(
                self._throttle_target - self._throttle_delta * 3, 0.0, +1.)
            if self._throttle_target <= 0:
                self._braking_target = np.clip(
                    self._braking_target + self._braking_delta, 0.0, +1.0)

        # Right
        elif key == 1:
            self._steering_target = np.clip(
                self._steering_target + self._steering_delta, -1.0, +1.)

        # Left
        elif key == 3:

            self._steering_target = np.clip(
                self._steering_target - self._steering_delta, -1.0, +1.)
        else:
            raise ValueError(
                f"Got key type of '{key}'. Was expecting one of the following: {', '.join(allowed_keys)}")


class WAMatplotlibController(_WAKeyboardController):
    """Controls a vehicle via keyboard input from a matplotlib figure

    Will asynchronously change inputs based on user input to the matplotlib window.

    Args:
        system (WASystem): The system used to manage the simulation
        vehicle_inputs (WAVehicleInputs): The vehicle inputs
        vis (WAMatplotlibVisualization): The visualization that holds a matplotlib figure
    """

    def __init__(self, system: 'WASystem', vehicle_inputs: 'WAVehicleInputs', vis: 'WAMatplotlibVisualization'):
        _check_type(vis, WAMatplotlibVisualization, 'vis',
                    'WAMatplotlibController::__init__')

        super().__init__(system, vehicle_inputs)

        vis.register_key_press_event(self._key_press)

        self._input_dict = {'up': 0, 'right': 1, 'down': 2, 'left': 3}

    def synchronize(self, time):
        """Synchronize the controller at the specified time

        Doesn't do anything since this controller is completely asynchronous

        Args:
                time (float): the time at which the controller should synchronize all depends to
        """
        pass

    def _key_press(self, value):
        if value in self._input_dict.keys():
            self._update(self._input_dict[value])


class WAROS2Controller(WAController):
    """Controller that communicates with a ROS2 control stack

    Raises:
        ImportError: Will be raised if ROS 2 is not found on the system.
    """

    def __init__(self, system: 'WASystem', vehicle_inputs: 'WAVehicleInputs'):
        super().__init__(system, vehicle_inputs)

        # Check if ROS 2 is installed
        try:
            import rclpy
        except ImportError:
            raise ImportError("ROS 2 was not found on the system.")

    def synchronize(self, time: float):
        pass

    def advance(self, step: float):
        pass
