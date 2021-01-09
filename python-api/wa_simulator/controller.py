"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

from abc import ABC, abstractmethod  # Abstract Base Class

# Other imports
import sys, tty, termios, atexit
from select import select
from numpy import clip, ceil


class WAVehicleInputs:
    """Object used to hold the inputs to the vehicle model

    The value ranges for the vehicle inputs may vary depending on the
    used vehicle model (i.e. radians vs percentages). This class is not reponsible for
    maintaining such properties, simply should be used for passing values around.

    Args:
                steering (double, optional): steering input. Defaults to 0.0.
                throttle (double, optional): throttle input. Defaults to 0.0.
                braking (double, optional): braking input. Defaults to 0.0.
    """

    def __init__(self, steering=0.0, throttle=0.0, braking=0.0):
        self.steering = steering
        self.throttle = throttle
        self.braking = braking


class WAController(ABC):
    """Base class for a controller

    Controllers are responsible for outputing a steering, throttle and braking value.
    This is done because in real life, those are the inputs our cars will have. The
    derived controller's (i.e. the new class that inherits from this class)
    responsibility is to take inputs from the simulation and return these values
    through the GetInputs method.

    Args:
                system (ChSystem): The system used to manage the simulation

    Attributes:
                inputs (WAVehicleInputs): Inputs to the vehicle model
    """

    def __init__(self, system):
        self.system = system
        self.inputs = WAVehicleInputs()

    @abstractmethod
    def Synchronize(self, time):
        """Synchronize the controller at the specified time

        Function is primarily as a semantic separation between different functionality.
        Most of the time, all controller logic can be placed in the Advance method. ROS would
        be a good example of an element that would publish in the Synchronize method and have
        other logic in the Advance method.

        Args:
                time (double): the time at which the controller should synchronize all depends to
        """
        pass

    @abstractmethod
    def Advance(self, step):
        """Advance the controller by the specified step

        Args:
                step (double): the time step at which the controller should be advanced
        """
        pass

    def GetInputs(self):
        """Get the vehicle inputs

        Returns:
                WAVehicleInputs: The input class
        """
        return self.inputs

    def _get_steering(self):
        return self.inputs.steering

    def _get_throttle(self):
        return self.inputs.throttle

    def _get_braking(self):
        return self.inputs.braking

    def _set_steering(self, steering):
        self.inputs.steering = steering

    def _set_throttle(self, throttle):
        self.inputs.throttle = throttle

    def _set_braking(self, braking):
        self.inputs.braking = braking

    steering = property(_get_steering, _set_steering)
    throttle = property(_get_throttle, _set_throttle)
    braking = property(_get_braking, _set_braking)


class WASimpleController(WAController):
    """Simple controller designed to never change the inputs

    Can be used for situations where controlling the vehicle isn't actually necessary
    """

    def Advance(self, step):
        pass

    def Synchronize(self, time):
        pass


class WAKeyboardController(WAController):
    """Controls a vehicle via input from the terminal window.

    Uses the KeyGetter object to grab input from the user in the terminal window.
    Inherits from the WAController method

    Args:
        system (ChSystem): The system used to manage the simulation

    Attributes:
        key_getter (KeyGetter): The object used to grab input from the terminal
        steering_target (double): The target steering value.
        throttle_target (double): The target throttle value.
        braking_target (double): The target braking value.
        steering_delta (double): The delta steering value.
        throttle_delta (double): The delta throttle value.
        braking_delta (double): The delta braking value.
        steering_gain (double): The gain steering value.
        throttle_gain (double): The gain throttle value.
        braking_gain (double): The gain braking value.
    """

    class KeyGetter:
        """Gets user input from the terminal.

        Will look for different input from the command line. The terminal window
        must be active for this to work.

        TODO: Fairly confident this only works on UNIX.

        Attributes:
                fd (STDIN_FILENO): Integer file descriptor.
                new_term (list): tty attributes for the fd. Setting terminal settings.
                old_term (list): tty attributes for the fd. Restoring terminal settings.
        """

        def __init__(self):
            # Save the terminal settings
            self.fd = sys.stdin.fileno()
            self.new_term = termios.tcgetattr(self.fd)
            self.old_term = termios.tcgetattr(self.fd)

            # New terminal setting unbuffered
            self.new_term[3] = self.new_term[3] & ~termios.ICANON & ~termios.ECHO
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

            # Support normal-terminal reset at exit
            atexit.register(self.set_normal_term)

        def __call__(self):
            """Checks the terminal window for a user input.

            This method is called through key_getter_object(). Will check terminal
            window for arrow keys. Will exit if any other key is pressed.

            Returns:
                int: a value between [0,3] describing the arrow key pressed
            """
            dr, dw, de = select([sys.stdin], [], [], 0)
            if dr == []:
                return -1

            c = sys.stdin.read(3)[2]
            vals = [65, 67, 66, 68]

            if vals.count(ord(c)) == 0:
                self.set_normal_term()
                raise RuntimeError(f'"{ord(c)}" is not an arrow key.')

            return vals.index(ord(c))

        def set_normal_term(self):
            """Resets to normal terminal.  On Windows this is a no-op."""
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    def __init__(self, system):
        super().__init__(system)

        self.key_getter = self.KeyGetter()

        self.steering_target = 0
        self.throttle_target = 0
        self.braking_target = 0

        self.steering_delta = system.render_step_size / 0.25
        self.throttle_delta = system.render_step_size / 1.0
        self.braking_delta = system.render_step_size / 0.3

        self.steering_gain = 4.0
        self.throttle_gain = 4.0
        self.braking_gain = 4.0

    def SetSteeringDelta(self, steering_delta):
        """Sets the steering delta value

        Args:
            steering_delta (double): the new steering delta value
        """
        self.steering_delta = steering_delta

    def SetThrottleDelta(self, throttle_delta):
        """Sets the throttle delta value

        Args:
            throttle_delta (double): the new throttle delta value
        """
        self.throttle_delta = throttle_delta

    def SetBrakingDelta(self, braking_delta):
        """Sets the braking delta value

        Args:
            braking_delta (double): the new braking delta value
        """
        self.braking_delta = braking_delta

    def SetGains(steering_gain, throttle_gain, braking_gain):
        """Sets the controllers gains

        Args:
            steering_gain (double): the new steering gain
            throttle_gain (double): the new throttle gain
            braking_gain (double): the new braking gain
        """
        self.steering_gain = steering_gain
        self.throttle_gain = throttle_gain
        self.braking_gain = braking_gain

    def KeyCheck(self):
        """Get the key from the KeyGetter and update target values based on input.

        The updated target values are based off the delta values for that respective input.
        In this controller, input values are clipped at [-1,1] or [0,1].
        """
        try:
            key = self.key_getter()
            if key == -1:
                return
            elif key == 0:
                self.throttle_target = clip(
                    self.throttle_target + self.throttle_delta, 0.0, +1.0
                )
                if self.throttle_target > 0:
                    self.braking_target = clip(
                        self.braking_target - self.braking_delta * 3, 0.0, +1.0
                    )
            elif key == 2:
                self.throttle_target = clip(
                    self.throttle_target - self.throttle_delta * 3, 0.0, +1.0
                )
                if self.throttle_target <= 0:
                    self.braking_target = clip(
                        self.braking_target + self.braking_delta, 0.0, +1.0
                    )
            elif key == 1:
                self.steering_target = clip(
                    self.steering_target + self.steering_delta, -1.0, +1.0
                )
            elif key == 3:
                self.steering_target = clip(
                    self.steering_target - self.steering_delta, -1.0, +1.0
                )
            else:
                print("Key not recognized")
                return
        except Exception as e:
            print(e)
            return

    def Synchronize(self, time):
        """Synchronize the controller at the specified time

        Calls KeyCheck

        Args:
                time (double): the time at which the controller should synchronize all depends to
        """
        self.KeyCheck()

    def Advance(self, step):
        """Advance the controller by the specified step

        Integrates dynamics over some step range. If the original step is the same as the passed
        step value, the method is only run once.

        Args:
                step (double): the time step at which the controller should be advanced
        """
        # Integrate dynamics, taking as many steps as required to reach the value 'step'
        t = 0
        while t < step:
            h = step - t

            steering_deriv = self.steering_gain * (self.steering_target - self.steering)
            throttle_deriv = self.throttle_gain * (self.throttle_target - self.throttle)
            braking_deriv = self.braking_gain * (self.braking_target - self.braking)

            self.steering += h * steering_deriv
            self.throttle += h * throttle_deriv
            self.braking += h * braking_deriv

            t += h


class WAMultipleControllers(WAController):
    """Wrapper class for multiple controllers. Allows multiple controllers to be used.

    The input values for the model are grabbed from the first controller in the list.

    Args:
        controllers (list): List of controllers.
    """

    def __init__(self, controllers):
        self.controllers = controllers

    def Synchronize(self, time):
        """Synchronize each controller at the specified time

        Args:
            time (double): the time at which the controller should synchronize all modules
        """
        for ctr in self.controllers:
            ctr.Synchronize(time)

    def Advance(self, step):
        """Advance the state of each managed controller

        Args:
            step (double): the time step at which the controller should be advanced
        """
        for ctr in self.controllers:
            ctr.Advance(step)

    def GetInputs(self):
        """Get the vehicle inputs

        Overrides base class method. Will just grab the first controllers inputs.

        Returns:
                The input class
        """

        return self.controllers[0].GetInputs()