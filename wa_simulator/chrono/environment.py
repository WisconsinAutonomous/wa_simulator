"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# WA Simulator
from wa_simulator.utils import load_json, check_field
from wa_simulator.environment import WAEnvironment

# Chrono specific imports
import pychrono as chrono
import pychrono.vehicle as veh


def load_chrono_terrain_from_json(system: 'WAChronoSystem', filename: str):
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

    terrain = veh.RigidTerrain(system._system, chrono.GetChronoDataFile(t['Input File']))  # noqa

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


class WAChronoEnvironment(WAEnvironment):
    """The environment wrapper that's responsible for holding Chrono assets and the terrain

    TODO: Add assets from file

    Args:
        system (WASystem): the wa system that wraps a ChSystem
        filename (str): the json specification file describing the environment
    """

    # Global filenames for environment models
    EGP_ENV_MODEL_FILE = "environments/ev_grand_prix.json"

    def __init__(self, system: 'WAChronoSystem', filename: str):
        self._terrain = load_chrono_terrain_from_json(system, filename)

    def synchronize(self, time):
        self._terrain.Synchronize(time)

    def advance(self, step):
        self._terrain.Advance(step)
