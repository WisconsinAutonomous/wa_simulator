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
import numpy as np


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
                self.throttle_target = np.clip(
                    self.throttle_target + self.throttle_delta, 0.0, +1.0
                )
                if self.throttle_target > 0:
                    self.braking_target = np.clip(
                        self.braking_target - self.braking_delta * 3, 0.0, +1.0
                    )
            elif key == 2:
                self.throttle_target = np.clip(
                    self.throttle_target - self.throttle_delta * 3, 0.0, +1.0
                )
                if self.throttle_target <= 0:
                    self.braking_target = np.clip(
                        self.braking_target + self.braking_delta, 0.0, +1.0
                    )
            elif key == 1:
                self.steering_target = np.clip(
                    self.steering_target + self.steering_delta, -1.0, +1.0
                )
            elif key == 3:
                self.steering_target = np.clip(
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


class WAPIDController(WAController):
    """PID Controller that contains a lateral and longitudinal controller

    Uses the lateral controller for steering and longitudinal controller throttle/braking

    Args:
        lat_controller (WAPIDLateralController, optional): Lateral controller for steering. Defaults to None.
        long_controller (WAPIDLongitudinalController, optional): Longitudinal controller for throttle/braking. Defaults to None.

    Attributes:
        lat_controller (WAPIDLateralController): Lateral controller for steering
        long_controller (WAPIDLongitudinalController): Longitudinal controller for throttle/braking
    """

    def __init__(self, lat_controller=None, long_controller=None):
        self.vehicle = vehicle

        # Lateral controller (steering)
        if lat_controller is None:
            lat_controller = WAPIDLateralController(track.center)
            lat_controller.SetGains(Kp=0.4, Ki=0, Kd=0.25)
            lat_controller.SetLookAheadDistance(dist=5)
        self.lat_controller = lat_controller

        if long_controller is None:
            # Longitudinal controller (throttle and braking)
            long_controller = WAPIDLongitudinalController()
            long_controller.SetGains(Kp=0.4, Ki=0, Kd=0)
            long_controller.SetTargetSpeed(speed=15.0)
        self.long_controller = long_controller

    def Synchronize(self, time):
        """Synchronize each controller at the specified time

        Args:
            time (double): the time at which the controller should synchronize all modules
        """
        self.lat_controller.Synchronize(time)
        self.long_controller.Synchronize(time)

    def Advance(self, step):
        """Advance the state of each controller

        Args:
            step (double): the time step at which the controller should be advanced
        """
        self.lat_controller.Advance(step)
        self.long_controller.Advance(step)

    def GetInputs(self):
        """Get the vehicle inputs

        Overrides base class method. Grabs the steering from the lateral controller and the
        throttle and braking from the longitudinal controller

        Returns:
            WAVehicleInputs: The input class
        """
        self.steering = self.lat_controller.steering
        self.throttle = self.long_controller.throttle
        self.braking = self.long_controller.braking
        return WAVehicleInputs(
            self.steering,
            self.throttle,
            self.braking,
        )


class WAPIDLateralController(WAController):
    """Lateral (steering) controller which minimizes error using a PID

    Args:
        path (WAPath): the path the vehicle is attempting to follow
        vehicle (WAVehicle): the vehicle who has dynamics

    Attributes:
        path (WAPath): the path the vehicle is attempting to follow
        vehicle (WAVehicle): the vehicle who has dynamics
        Kp (double): proportional gain
        Ki (double): integral gain
        Kd (double): derivative gain
        dist (double): lookahead distance
        target (double): point on the path that is attempting to reach
        sentinel (double): some point a dist directly in front of the vehicle
        err (double): overall error
        errd (double): derivative error (not accumulated)
        erri (double): integral error accumulated over time
    """

    def __init__(self, path, vehicle):
        self.Kp = 0
        self.Ki = 0
        self.Kd = 0

        self.dist = 0
        self.target = np.array([0, 0, 0])
        self.sentinel = np.array([0, 0, 0])

        self.err = 0
        self.errd = 0
        self.erri = 0

        self.path = path
        self.vehicle = vehicle

    def SetGains(self, Kp, Ki, Kd):
        """Set the gains

        Args:
            Kp (double): new proportional gain
            Ki (double): new integral gain
            Kd (double): new derivative gain
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

    def SetLookAheadDistance(self, dist):
        """Set the lookahead distance

        Args:
            dist (double): new lookahead distance
        """
        self.dist = dist

    def Synchronize(self, time):
        """Synchronize the controller at the passed time

        Doesn't actually do anything.

        Args:
            time (double): the time to synchronize the controller to
        """
        pass

    def Advance(self, step):
        """Advance the state of the controller by step

        Args:
            step (double): step size to update the controller by
        """
        state = self.vehicle.GetSimpleState()
        self.sentinel = np.array(
            [
                self.dist * np.cos(state.yaw) + state.x,
                self.dist * np.sin(state.yaw) + state.y,
                0,
            ]
        )

        self.target = self.path.calcClosestPoint(self.sentinel)

        # The "error" vector is the projection onto the horizontal plane (z=0) of
        # vector between sentinel and target
        err_vec = self.target - self.sentinel
        err_vec.z = 0

        # Calculate the sign of the angle between the projections of the sentinel
        # vector and the target vector (with origin at vehicle location).
        sign = self.calcSign(state)

        # Calculate current error (magnitude)
        err = sign * err_vec.Length()

        # Estimate error derivative (backward FD approximation).
        self.errd = (err - self.err) / step

        # Calculate current error integral (trapezoidal rule).
        self.erri += (err + self.err) * step / 2

        # Cache new error
        self.err = err

        # Return PID output (steering value)
        self.steering = np.clip(
            self.Kp * self.err + self.Ki * self.erri + self.Kd * self.errd, -1.0, 1.0
        )

    def calcSign(self, state):
        """Calculate the sign of the angle between the projections of the sentinel vector
        and the target vector (with origin at vehicle location).

        Args:
            state (tuple): (x position, y position, yaw about the Z, speed)

        Returns:
            int: the sign indicating direction of the state and the sentinel on the path (-1 for left or 1 for right)
        """
        pos = np.array([state.x, state.y, 0])

        sentinel_vec = self.sentinel - pos
        target_vec = self.target - pos

        temp = np.dot(np.cross(sentinel_vec, target_vec), np.array([0, 0, 1]))

        return (temp > 0) - (temp < 0)


class WAPIDLongitudinalController(WAController):
    """Longitudinal (throttle, braking) controller which minimizes error using a PID

    Args:
        vehicle (WAVehicle): the vehicle who has dynamics

    Attributes:
        vehicle (WAVehicle): the vehicle who has dynamics
        Kp (double): proportional gain
        Ki (double): integral gain
        Kd (double): derivative gain
        err (double): overall error
        errd (double): derivative error (not accumulated)
        erri (double): integral error accumulated over time
        speed (double): the current speed
        target_speed (double): the target speed
        throttle_threshold (double): throttle position at which vehicle is moving too fast and the step size should decrease
    """

    def __init__(self, vehicle):
        self.Kp = 0
        self.Ki = 0
        self.Kd = 0

        self.err = 0
        self.errd = 0
        self.erri = 0

        self.speed = 0
        self.target_speed = 0

        self.throttle_threshold = 0.2

        self.vehicle = vehicle

    def SetGains(self, Kp, Ki, Kd):
        """Set the gains

        Args:
            Kp (double): new proportional gain
            Ki (double): new integral gain
            Kd (double): new derivative gain
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

    def SetTargetSpeed(self, speed):
        """Set the target speed for the controller

        Args:
            speed (double): the new target speed
        """
        self.target_speed = speed

    def Synchronize(self, time):
        """Synchronize the controller at the passed time

        Doesn't actually do anything.

        Args:
            time (double): the time to synchronize the controller to
        """
        pass

    def Advance(self, step):
        """Advance the state of the controller by step

        Args:
            step (double): step size to update the controller by
        """

        self.speed = self.vehicle.GetSimpleState().v

        # Calculate current error
        err = self.target_speed - self.speed

        # Estimate error derivative (backward FD approximation)
        self.errd = (err - self.err) / step

        # Calculate current error integral (trapezoidal rule).
        self.erri += (err + self.err) * step / 2

        # Cache new error
        self.err = err

        # Return PID output (steering value)
        throttle = np.clip(
            self.Kp * self.err + self.Ki * self.erri + self.Kd * self.errd, -1.0, 1.0
        )

        if throttle > 0:
            # Vehicle moving too slow
            self.braking = 0
            self.throttle = throttle
        elif self.target_throttle > self.throttle_threshold:
            # Vehicle moving too fast: reduce throttle
            self.braking = 0
            self.throttle = self.target_throttle + throttle
        else:
            # Vehicle moving too fast: apply brakes
            self.braking = -throttle
            self.throttle = 0