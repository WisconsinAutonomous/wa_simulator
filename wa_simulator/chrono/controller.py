"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# WA Simulator
from wa_simulator.controller import WAController, WAVehicleInputs

# Chrono imports
import pychrono.vehicle as veh

# Other imports
import numpy as np


class WAIrrlichtController(WAController):
    """Wrapper for a ChIrrGuiDriver.

    Uses the keyboard in the irrlicht window to control the car. Window must be active
    to work. Currently not supported on Mac when the anaconda build is used

    Args:
        visualization (WAIrrlichtVisualization): the irrlicht visualization
        system (WASystem): the system
    """

    def __init__(self, visualization, system):
        # Create the interactive driver
        driver = veh.ChIrrGuiDriver(visualization.app)

        render_step_size = system.render_step_size

        # Set the time response for steering and throttle keyboard inputs.
        steering_time = 1.0  # time to go from 0 to +1 (or from 0 to -1)
        throttle_time = 1.0  # time to go from 0 to +1
        braking_time = 0.3  # time to go from 0 to +1
        driver.SetSteeringDelta(render_step_size / steering_time)
        driver.SetThrottleDelta(render_step_size / throttle_time)
        driver.SetBrakingDelta(render_step_size / braking_time)

        driver.Initialize()

        self.driver = driver

    def synchronize(self, time):
        """Synchronize the irrlicht driver at the specified time

        Args:
            time (double): time to synchronize at
        """
        self.driver.Synchronize(time)

    def advance(self, step):
        """Advance the irrlicht driver by the specified step

        Args:
            step (double): step to advance by
        """
        self.driver.Advance(step)

    def get_inputs(self):
        """Get the vehicle inputs

        Overrides base class method. Converts a veh.DriverInputs to a WAVehicleInputs

        Returns:
                The input class
        """
        inputs = self.driver.GetInputs()
        return WAVehicleInputs(
            inputs.m_steering,
            inputs.m_throttle,
            inputs.m_braking,
        )