"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

from .controller import WAController  # WA Simulator


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