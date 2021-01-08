"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

from abc import ABC, abstractmethod  # Abstract Base Class


class WAEnvironment(ABC):
    """Base class for the environment object.

    The environment object is responsible for handling data or assets within the world.
    """

    @abstractmethod
    def Synchronize(self, time):
        """Synchronize the environment at the specified time

        Function is primarily as a semantic separation between different functionality.
        Most of the time, all environment logic can be placed in the Advance method.

        Args:
                time (double): the time at which the environment should synchronize all depends to
        """
        pass

    @abstractmethod
    def Advance(self, step):
        """Advance the environment by the specified step

        Args:
                step (double): the time step at which the environment should be advanced
        """
        pass
