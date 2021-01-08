"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# WA Simulator
from .visualization import WAVisualization


class WAMultipleVisualizations(WAVisualization):
    """Wrapper class for multiple visualizations. Allows multiple visualizations to be used.

    Args:
        visualizations (list): List of visualizations.
    """
    def __init__(self, visualizations):
        self.visualizations = visualizations

    def Synchronize(self, time, vehicle_inputs):
        """Synchronize each visualization at the specified time

        Args:
            time (double): the time at which the visualization should synchronize all modules
            vehicle_inputs (WAVehicleInputs): vehicle inputs
        """
        for vis in self.visualizations:
            vis.Synchronize(time, vehicle_inputs)

    def Advance(self, step):
        """Advance the state of each managed visualization

        Args:
            step (double): the time step at which the visualization should be advanced
        """
        for vis in self.visualizations:
            vis.Advance(step)
