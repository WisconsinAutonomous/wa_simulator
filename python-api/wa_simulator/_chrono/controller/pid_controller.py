# WA Simulator
from wa_simulator.controller.controller import WAController

import pychrono as chrono
import numpy as np
import math

class PIDController:
    def __init__(self, lat_controller=None, long_controller=None):
        # Lateral controller (steering)
        if lat_controller is None:
            lat_controller = PIDLateralController(track.center)
            lat_controller.SetGains(Kp=0.4, Ki=0, Kd=0.25)
            lat_controller.SetLookAheadDistance(dist=5)
        self.lat_controller = lat_controller

        if long_controller is None:
            # Longitudinal controller (throttle and braking)
            long_controller = PIDLongitudinalController()
            long_controller.SetGains(Kp=0.4, Ki=0, Kd=0)
            long_controller.SetTargetSpeed(speed=15.0)
        self.long_controller = long_controller

    def GetTargetAndSentinel(self):
        return self.lat_controller.target, self.lat_controller.sentinel

    def Advance(self, step, vehicle):
        self.steering = self.lat_controller.Advance(step, vehicle)
        self.throttle, self.braking = self.long_controller.Advance(step, vehicle)
        return self.steering, self.throttle, self.braking

class PIDLateralController:
    def __init__(self, path):
        self.Kp = 0
        self.Ki = 0
        self.Kd = 0

        self.dist = 0
        self.target = np.array([0,0,0])
        self.sentinel = np.array([0,0,0])

        self.steering = 0

        self.err = 0
        self.errd = 0
        self.erri = 0

        self.path = path

    def SetGains(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

    def SetLookAheadDistance(self, dist):
        self.dist = dist

    def Advance(self, step, vehicle):
        state = vehicle.GetState()
        self.sentinel = np.array([
            self.dist * math.cos(state.yaw) + state.x,
            self.dist * math.sin(state.yaw) + state.y,
            0]
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

        vehicle.driver.SetTargetSteering(self.steering)

        return self.steering

    def calcSign(self, state):
        """
        Calculate the sign of the angle between the projections of the sentinel vector
        and the target vector (with origin at vehicle location).
        """

        sentinel_vec = self.sentinel - state.pos
        target_vec = self.target - state.pos

        temp = (sentinel_vec % target_vec) ^ chrono.ChVectorD(0, 0, 1)

        return (temp > 0) - (temp < 0)


class PIDLongitudinalController:
    def __init__(self):
        self.Kp = 0
        self.Ki = 0
        self.Kd = 0

        self.err = 0
        self.errd = 0
        self.erri = 0

        self.speed = 0
        self.target_speed = 0

        self.throttle_threshold = 0.2

    def SetGains(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

    def SetTargetSpeed(self, speed):
        self.target_speed = speed

    def Advance(self, step, vehicle):
        self.speed = vehicle.GetState().v

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
        elif vehicle.driver.GetTargetThrottle() > self.throttle_threshold:
            # Vehicle moving too fast: reduce throttle
            self.braking = 0
            self.throttle = vehicle.driver.GetTargetThrottle() + throttle
        else:
            # Vehicle moving too fast: apply brakes
            self.braking = -throttle
            self.throttle = 0

        vehicle.driver.SetTargetThrottle(self.throttle)
        vehicle.driver.SetTargetBraking(self.braking)

        return self.throttle, self.braking