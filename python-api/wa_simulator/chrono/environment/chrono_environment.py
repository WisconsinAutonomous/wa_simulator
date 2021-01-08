"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# WA Simulator
from wa_simulator.environment.environment import WAEnvironment
from wa_simulator.chrono.environment.chrono_terrain import WAChronoTerrain

# Chrono specific imports
import pychrono as chrono


class WAChronoEnvironment(WAEnvironment):
    """The environment wrapper that's responsible for holding Chrono assets and the terrain

    TODO: Add assets

    Args:
        filename (str): the json specification file describing the environment
        system (WASystem): the wa system that wraps a ChSystem
        terrain (ChTerrain, optional): a chrono terrain. Will create one if not passed. Defaults to None.

    Attributes:
        EGP_ENV_MODEL_FILE (str): evGrand Prix environment file
        IAC_ENV_MODEL_FILE (str): IAC environment file
        terrain (WAChronoTerrain): the wrapper for the chrono terrain
    """

    # Global filenames for environment models
    EGP_ENV_MODEL_FILE = "environments/ev_grand_prix.json"
    IAC_ENV_MODEL_FILE = "environments/iac.json"

    def __init__(self, filename, system, terrain=None):
        if terrain is None:
            terrain = WAChronoTerrain(filename, system)

        self.terrain = terrain

    def Synchronize(self, time):
        """Synchronize the environment. Will just synchronize the terrain

        Args:
            time ([type]): [description]
        """
        self.terrain.Synchronize(time)

    def Advance(self, step):
        """Advance the environment by the step size. Will just advance the terrain.

        Args:
            step (double): the step size to update the environment by
        """
        self.terrain.Advance(step)
