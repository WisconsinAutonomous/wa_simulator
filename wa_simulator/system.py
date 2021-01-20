"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

from abc import ABC, abstractmethod  # Abstract Base Class


class WASystem(ABC):
    """Used to manage simulation parameters and can be used to update simulation dynamics

    A system is used for organizational purposes almost exclusively. It is passed to other
    module classes to handle passing various attributes. Could be responsible for updating
    module dynamics depending on the underlying models.

    Args:
        step_size (double): the step size for the simulation
        render_step_size (double, optional): Render step size. Defaults to 2e-2.

    Attributes:
        step_number (int): Counter of the Advance function
        step_size (double): the step size for the simulation
        render_step_size (double): the render step size
        time (double): stores the time from the simulation
    """

    def __init__(self, step_size, render_step_size=2e-2):
        self.step_number = 0
        self.step_size = step_size
        self.render_step_size = render_step_size

        self.time = 0

    def advance(self):
        """Advance the system

        Will update the time and increment the step number
        """
        self.time += self.step_size
        self.step_number += 1

    def get_sim_time(self):
        """Get the simulation time

        Returns:
            double: the simulation time
        """
        return self.time

    def get_step_number(self):
        """Get the step number

        Returns:
            int: the step number
        """
        return self.step_number
