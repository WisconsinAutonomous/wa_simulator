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
    def synchronize(self, time):
        """Synchronize the environment at the specified time

        Function is primarily as a semantic separation between different functionality.
        Most of the time, all environment logic can be placed in the Advance method.

        Args:
                time (double): the time at which the environment should synchronize all depends to
        """
        pass

    @abstractmethod
    def advance(self, step):
        """Advance the environment by the specified step

        Args:
                step (double): the time step at which the environment should be advanced
        """
        pass


class WASimpleEnvironment(WAEnvironment):
    """Simple environment that doesn't have any assets within the world.

    Args:
        filename (str): filename
        sys (WASystem): system
    """

    # Global filenames for environment models
    EGP_ENV_MODEL_FILE = "environments/ev_grand_prix.json"
    IAC_ENV_MODEL_FILE = "environments/iac.json"

    def __init__(self, filename, sys):
        pass

    def synchronize(self, time):
        """Synchronize the environment with the rest of the world at the specified time

        Doesn't actually do anything.

        Args:
            time (double): the time at which the enviornment should be synchronized to
        """
        pass

    def advance(self, step):
        """Advance the state of the environment

        Doesn't actually do anything.

        Args:
            step (double): the time step at which the enviornment should be advanced
        """
        pass
