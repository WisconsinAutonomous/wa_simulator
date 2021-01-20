"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

from abc import ABC, abstractmethod  # Abstract Base Class


class WATerrain(ABC):
    """Base class for the terrain object

    Maintains knowledge of the terrain or "ground" that a vehicle interacts with.
    """

    @abstractmethod
    def synchronize(self, time):
        """Synchronize the terrain at the specified time

        Function is primarily as a semantic separation between different functionality.
        Most of the time, all terrain logic can be placed in the Advance method.

        Args:
                time (double): the time at which the terrain should synchronize all depends to
        """
        pass

    @abstractmethod
    def advance(self, step):
        """Advance the terrain by the specified step

        Args:
                step (double): the time step at which the terrain should be advanced
        """
        pass
