"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

from abc import abstractmethod  # Abstract Base Class

# WA Simulator
from wa_simulator.base import WABase


class WAEnvironment(WABase):
    """Base class for the environment object.

    The environment object is responsible for handling data or assets within the world.
    Assets may be obstacles, miscellaneous objects, other vehicles or weather.
    """

    @abstractmethod
    def synchronize(self, time: float):
        pass

    @abstractmethod
    def advance(self, step: float):
        pass

    def is_ok(self) -> bool:
        return True


class WASimpleEnvironment(WAEnvironment):
    """Simple environment that doesn't have any assets within the world."""

    # Global filenames for environment models
    EGP_ENV_MODEL_FILE = "environments/ev_grand_prix.json"

    def __init__(self):
        pass

    def synchronize(self, time: float):
        """Synchronize the environment with the rest of the world at the specified time

        Simple environment doesn't actually do anything for now.

        Args:
            time (float): the time at which the enviornment should be synchronized to
        """
        pass

    def advance(self, step: float):
        """Advance the state of the environment

        Simple environment doesn't actually do anything for now.

        Args:
            step (float): the time step at which the enviornment should be advanced
        """
        pass
