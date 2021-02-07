"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# WA Simulator
from wa_simulator.chrono.utilities import str_list_to_ChVectorF
from wa_simulator.chrono.system import WAChronoSystem

# Chrono specific imports
import pychrono as chrono
import pychrono.sensor as sens


def load_scene_from_json(filename: str, manager: sens.ChSensorManager):
    scene_filename = chrono.GetChronoDataFile(filename)

    with open(filename) as f:
        j = json.load(f)

    if "World" in j:
        if "Point Lights" in j["World"]:
            for point_light in j["World"]["Point Lights"]:
                pos = str_list_to_ChVectorF(point_light["Position"])
                color = str_list_to_ChVectorF(point_light["Color"])
                max_range = float(point_light["Maximum Range"])

                manager.scene.AddPointLight(pos, color, max_range)


class WASensorManager:

    # Global filenames for environment models
    EGP_SCENE_FILE = "sensors/scenes/ev_grand_prix.json"

    def __init__(self, system: WAChronoSystem, filename: str = None):
        if not isinstance(system, WAChronoSystem):
            raise TypeError('WASensorManager takes a WAChronoSystem.')

        self.system = system

        self.manager = sens.ChSensorManager(self.system.system)

        if filename is not None:
            load_scene_from_json(filename, self.manager)

    def add_sensor(self, filename: str, parent: chrono.ChBody, offset_pose: chrono.ChFrame):
        sensor_filename = chrono.GetChronoDataFile(filename)
        sensor = sens.CreateFromJSON(sensor_filename, parent, offset_pose)
        self.manager.AddSensor(sensor)
