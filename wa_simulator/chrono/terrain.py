"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# WA Simulator
from wa_simulator.terrain import WATerrain

# Chrono specific imports
import pychrono as chrono
import pychrono.vehicle as veh


def read_terrain_model_file(filename):
    """Get the json specification file describing a ChTerrain

    Args:
        filename (str): the relative path to a terrain json file

    Returns:
        str: the absolute json file
    """
    import json

    full_filename = chrono.GetChronoDataFile(filename)

    with open(full_filename) as f:
        j = json.load(f)

    if "Terrain" not in j:
        print("'Terrain' not present in the passed json file.")
        exit()
    terrain_filename = chrono.GetChronoDataFile(j["Terrain"]["Input File"])

    return terrain_filename


class WAChronoTerrain(WATerrain):
    """Wrapper for a ChTerrain

    Only support for RigidTerrain is supported for now.

    Args:
        filename (str): the json specification file describing the terrain
        system (WASystem): system used to create the terrain

    Attributes:
        terrain (RigidTerrain): the created rigid terrain
    """

    def __init__(self, filename, system):
        # Get the filenames
        terrain_filename = read_terrain_model_file(filename)

        # Create the terrain
        self.terrain = veh.RigidTerrain(system.system, terrain_filename)

    def synchronize(self, time):
        """Synchronize the terrain at the specified time

        Args:
            time (double): time at which synchronization should occur
        """
        self.terrain.Synchronize(time)

    def advance(self, step):
        """Advance the terrain dynamics by the specified step

        Args:
            step (double): the step at which the simulation should be updated by
        """
        self.terrain.Advance(step)