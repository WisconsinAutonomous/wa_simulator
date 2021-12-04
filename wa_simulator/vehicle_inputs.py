"""
Wisconsin Autonomous - https://wa.wisc.edu

Copyright (c) 2021 wa.wisc.edu
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
        steering (float, optional): steering input. Defaults to 0.0.
        throttle (float, optional): throttle input. Defaults to 0.0.
        braking (float, optional): braking input. Defaults to 0.0.

    Attributes:
        steering (float): steering input. 
        throttle (float): throttle input. 
        braking (float): braking input. 
    """

    def __init__(self, steering: float = 0.0, throttle: float = 0.0, braking: float = 0.0):
        self.steering = steering
        self.throttle = throttle
        self.braking = braking
