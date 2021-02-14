"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# WA Simulator
from wa_simulator.utils import load_json, check_field
from wa_simulator.terrain import WATerrain
from wa_simulator.chrono.system import WAChronoSystem

# Chrono specific imports
import pychrono as chrono
import pychrono.vehicle as veh


def load_chrono_terrain_from_json(filename: str, system: WAChronoSystem):
    """Load a ChTerrain from a json specification file

    Args:
        filename (str): the relative path to a terrain json file
        system (WAChronoSystem): the chrono system used to handle the terrain

    Returns:
        ChTerrain: The loaded terrain
    """
    j = load_json(chrono.GetChronoDataFile(filename))

    # Validate the json file
    check_field(j, 'Terrain', field_type=dict)

    t = j['Terrain']
    check_field(t, 'Input File', field_type=str)
    check_field(t, 'Texture', field_type=str, optional=True)

    terrain = veh.RigidTerrain(system.system, chrono.GetChronoDataFile(t['Input File']))  # noqa

    # Add texture to the terrain, if desired
    if 'Texture' in t:
        texture_filename = chrono.GetChronoDataFile(t['Texture'])

        vis_mat = chrono.ChVisualMaterial()
        vis_mat.SetKdTexture(texture_filename)
        vis_mat.SetSpecularColor(chrono.ChVectorF(0.0, 0.0, 0.0))
        vis_mat.SetFresnelMin(0)
        vis_mat.SetFresnelMax(0.1)

        patch_asset = terrain.GetPatches()[0].GetGroundBody().GetAssets()[0]
        patch_visual_asset = chrono.CastToChVisualization(patch_asset)
        patch_visual_asset.material_list.append(vis_mat)

    return terrain


class WAChronoTerrain(WATerrain):
    """Wrapper for a ChTerrain

    Only support for RigidTerrain is supported for now.

    Args:
        filename (str): the json specification file describing the terrain
        system (WAChronoSystem): system used to create the terrain

    Attributes:
        terrain (RigidTerrain): the created rigid terrain
    """

    def __init__(self, filename, system: WAChronoSystem):
        self.terrain = load_chrono_terrain_from_json(filename, system)

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
