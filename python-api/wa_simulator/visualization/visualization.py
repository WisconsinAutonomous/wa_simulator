"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

from abc import ABC, abstractmethod  # Abstract Base Class


class WAVisualization(ABC):
    """Base class to be used for visualization of the simulation world.

    Derived classes will use various world attributes to visualize the simulation
    """

    @abstractmethod
    def Synchronize(self, time, vehicle_inputs):
        """Synchronize the visualization at the specified time with the passed vehicle inputs

        Args:
            time (double): time to synchronize the visualization to
            vehicle_inputs (WAVehicleInputs): inputs to the vehicle. Can be helpful for visualization (debug) purposes.
        """
        pass

    @abstractmethod
    def Advance(self, step):
        """Advance the state of the visualization by the specified step

        Args:
            step (double): step size to update the visualization by
        """
        pass

    @abstractmethod
    def IsOk(self):
        """Verifies the visualization is running properly.

        Returns:
            bool: Whether the visualization is running correctly.
        """
        pass
