"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""


class WASystem:
    """Used to manage simulation parameters and can be used to update simulation dynamics

    A system is used for organizational purposes almost exclusively. It is passed to other
    module classes to handle passing various attributes. Could be responsible for updating
    module dynamics depending on the underlying models.

    Args:
        step_size (float): the step size for the simulation. Defaults to 3e-3.
        render_step_size (float, optional): Render step size. Defaults to 2e-2.

    Attributes:
        step_number (int): Counter of the Advance function
        step_size (float): the step size for the simulation
        render_step_size (float): the render step size
        time (float): stores the time from the simulation
    """

    def __init__(self, step_size: float = 3e-3, render_step_size: float = 2e-2):
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
