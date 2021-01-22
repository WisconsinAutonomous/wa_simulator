"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""


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
