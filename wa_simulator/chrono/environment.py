"""
Wisconsin Autonomous - https://wa.wisc.edu

Copyright (c) 2021 wa.wisc.edu
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# WA Simulator
from wa_simulator.core import WA_PI
from wa_simulator.utils import _load_json, _check_field, _WAStaticAttribute, get_wa_data_file
from wa_simulator.environment import WAEnvironment, load_environment_from_json, WABody
from wa_simulator.chrono.utils import ChVector_to_WAVector, WAVector_to_ChVector, get_chrono_data_file

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
    j = _load_json(filename)

    # Validate the json file
    _check_field(j, 'Terrain', field_type=dict)

    t = j['Terrain']
    _check_field(t, 'Input File', field_type=str)
    _check_field(t, 'Texture', field_type=str, optional=True)

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
    _EGP_ENV_MODEL_FILE = "environments/ev_grand_prix.json"

    EGP_ENV_MODEL_FILE = _WAStaticAttribute(
        '_EGP_ENV_MODEL_FILE', get_chrono_data_file)

    def __init__(self, system: 'WAChronoSystem', filename: str):
        super().__init__()

        self._system = system
        self._terrain = load_chrono_terrain_from_json(system, filename)

        load_environment_from_json(self, filename)

    def synchronize(self, time):
        self._terrain.Synchronize(time)

    def advance(self, step):
        self._terrain.Advance(step)

        for asset in self._updating_assets:
            asset.chrono_body.SetPos(WAVector_to_ChVector(asset.position))

    def add_asset(self, asset: 'Any'):
        if isinstance(asset, chrono.ChBody):
            self._system._system.AddBody(asset)
            return
        if isinstance(asset, WABody):
            if not hasattr(asset, 'size') or not hasattr(asset, 'position'):
                raise AttributeError(
                    "Body must have 'size', and 'position' fields")

            position = asset.position
            yaw = 0 if not hasattr(asset, 'yaw') else asset.yaw
            size = asset.size

            body_type = 'box'
            if hasattr(asset, 'body_type'):
                body_type = asset.body_type

            if body_type == 'sphere':
                body = chrono.ChBodyEasySphere(size.length, 1000, True, False)
                body.SetBodyFixed(True)
            elif body_type == 'box':
                body = chrono.ChBodyEasyBox(
                    size.x, size.y, size.z, 1000, True, False)
                body.SetBodyFixed(True)
            else:
                raise ValueError(
                    f"'{asset.body_type}' not a supported body type.")

            body.SetPos(WAVector_to_ChVector(position))
            body.SetRot(chrono.Q_from_AngZ(-yaw + WA_PI / 2))

            if hasattr(asset, 'color'):
                color = asset.color
                body.AddAsset(chrono.ChColorAsset(
                    chrono.ChColor(color.x, color.y, color.z)))

                texture = chrono.ChVisualMaterial()
                texture.SetDiffuseColor(
                    chrono.ChVectorF(color.x, color.y, color.z))
                chrono.CastToChVisualization(
                    body.GetAssets()[0]).material_list.append(texture)

            if hasattr(asset, 'texture'):
                texture = chrono.ChVisualMaterial()
                texture.SetKdTexture(get_wa_data_file(asset.texture))
                chrono.CastToChVisualization(
                    body.GetAssets()[0]).material_list.append(texture)

            self._system._system.AddBody(body)

            asset.chrono_body = body

        super().add_asset(asset)
