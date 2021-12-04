"""
Wisconsin Autonomous - https://wa.wisc.edu

Copyright (c) 2021 wa.wisc.edu
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# WA Simulator
from wa_simulator.core import WAVector, WA_PI
from wa_simulator.utils import get_wa_data_file
from wa_simulator.path import WAPath
from wa_simulator.track import WATrack
from wa_simulator.visualization import WAVisualization, WABody
from wa_simulator.vehicle_inputs import WAVehicleInputs
from wa_simulator.chrono.utils import ChVector_to_WAVector, WAVector_to_ChVector

# Chrono specific imports
import pychrono as chrono
import pychrono.vehicle as veh
import pychrono.irrlicht as irr

# Other imports
import numpy as np
from math import ceil


def draw_path_in_irrlicht(system: 'WAChronoSystem', path: 'WAPath'):
    """Draw a WAPath representation as a ChBezierCurve in irrlicht

    Basically just copies over the path's points into something viewable for Chrono

    Args:
        system (WAChronoSystem): system that manages the simulation
        path (WAPath): WA path object to visualize in irrlicht
    """
    points = path.get_points()
    ch_points = chrono.vector_ChVectorD()
    for p in points:
        ch_points.push_back(chrono.ChVectorD(p[0], p[1], p[2]))
    curve = chrono.ChBezierCurve(ch_points)

    road = system._system.NewBody()
    road.SetBodyFixed(True)
    system._system.AddBody(road)

    num_points = len(points)
    path_asset = chrono.ChLineShape()
    path_asset.SetLineGeometry(chrono.ChLineBezier(curve))
    path_asset.SetColor(chrono.ChColor(0, 0.8, 0))
    path_asset.SetNumRenderPoints(max(2 * num_points, 400))
    road.AddAsset(path_asset)


def create_sphere_in_chrono(system: 'WAChronoSystem', rgb=(1, 0, 0)) -> chrono.ChBodyEasySphere:
    """Create and add a sphere to the chrono world 

    Args:
        system (WASystem): the system that manages the simulation
        rgb (tuple, optional): (red, green, blue). Defaults to (1, 0, 0) or red.

    Returns:
        chrono.ChBodyEasySphere: the sphere that was created
    """
    sphere = chrono.ChBodyEasySphere(0.25, 1000, True, False)
    sphere.SetBodyFixed(True)
    sphere.AddAsset(chrono.ChColorAsset(*rgb))

    texture = chrono.ChVisualMaterial()
    texture.SetDiffuseColor(chrono.ChVectorF(*rgb))
    chrono.CastToChVisualization(sphere.GetAssets()[0]).material_list.append(texture)

    system._system.Add(sphere)

    return sphere


def update_position_of_sphere(sphere: chrono.ChBodyEasySphere, pos: WAVector):
    """Update the position of a sphere being visualized in irrlicht

    Args:
        sphere (chrono.ChBodyEasySphere): the sphere to change the position of
        pos (WAVector): the new position
    """
    if not isinstance(pos, WAVector):
        pos = WAVector(pos)

    sphere.SetPos(chrono.ChVectorD(pos.x, pos.y, 0))


class WAChronoIrrlicht(WAVisualization):
    """Chrono irrlicht visualization wrapper. Sets default values for a Vehicle irr app

    Args:
        system (WAChronoSystem): holds information regarding the simulation and performs dynamic updates
        vehicle (WAChronoVehicle): vehicle that holds the Chrono vehicle
        vehicle_inputs (WAVehicleInputs): the vehicle inputs
        environment (WAEnvironment, optional): An environment with various world assets to visualize. Defaults to None (doesn't visualize anything).
        opponents (list, optional): Opponents present in the simulation. The camera will track :attr:`~vehicle` not any opponent.
        record (bool, optional): If set to true, images will be saved under record_filename. Defaults to False (doesn't save images).
        record_folder (str, optional): The folder to save images to. Defaults to "OUTPUT/".
        should_bind (bool, optional): After `all` assets have been added to the environment, irrlicht needs to "bind" and add the assets to the 3D rendered world. This can be done either on instantiation (True) or on the first update (False). Defaults to True.
    """

    def __init__(self, system: 'WAChronoSystem', vehicle: 'WAChronoVehicle', vehicle_inputs: 'WAVehicleInputs', environment: 'WAEnvironment' = None, opponents: list = [], record: bool = False, record_folder: str = "OUTPUT/", should_bind: bool = True):
        self._render_steps = int(
            ceil(system.render_step_size / system.step_size))

        self._system = system
        self._vehicle_inputs = vehicle_inputs

        self._record = record
        self._record_folder = record_folder
        self._save_number = 0

        self._app = veh.ChVehicleIrrApp(vehicle._vehicle)
        self._app.SetHUDLocation(500, 20)
        self._app.SetSkyBox()
        self._app.AddTypicalLogo()
        self._app.AddTypicalLights(
            irr.vector3df(-150.0, -150.0, 200.0),
            irr.vector3df(-150.0, 150.0, 200.0),
            100,
            100,
        )
        self._app.AddTypicalLights(
            irr.vector3df(150.0, -150.0, 200.0),
            irr.vector3df(150.0, 150.0, 200.0),
            100,
            100,
        )
        self._app.SetChaseCamera(chrono.ChVectorD(0.0, 0.0, 1.75), 6.0, 0.5)
        self._app.SetTimestep(system.step_size)

        self._first = True
        if should_bind:
            self.bind()

        if environment is not None:
            self.visualize(environment.get_assets())

    def synchronize(self, time: float):
        """Synchronize the irrlicht app with the vehicle inputs at the passed time

        Args:
            time (double): time to synchronize the simulation to
        """
        d = veh.Inputs()
        d.m_steering = self._vehicle_inputs.steering
        d.m_throttle = self._vehicle_inputs.throttle
        d.m_braking = self._vehicle_inputs.braking

        self._app.Synchronize("", d)

    def advance(self, step: float):
        """Advance the state of the visualization by the specified step

        Will update the render only if the simulation step is a multiple of render steps

        Args:
            step (double): step size to update the visualization by
        """
        if self._first:
            self.bind()

        if self._system.step_number % self._render_steps == 0:
            self._app.BeginScene(True, True, irr.SColor(255, 140, 161, 192))
            self._app.DrawAll()
            self._app.EndScene()

            if self._record:
                self._app.WriteImageToFile(f"{self._record_folder}{self._save_number}.png")
                self._save_number += 1

        self._app.Advance(step)

    def is_ok(self):
        """Checks if the irrlicht rending window is still alive

        Returns:
            bool: whether the simulation is still alive
        """
        return self._app.GetDevice().run()

    def bind(self):
        """Call AssetBindAll and AssetUpdateAll."""
        self._app.AssetBindAll()
        self._app.AssetUpdateAll()

        self._first = False

    def visualize(self, assets, *args, **kwargs):
        for i, asset in enumerate(assets):
            if isinstance(asset, WAPath):
                draw_path_in_irrlicht(self._system, asset)
            elif isinstance(asset, WATrack):
                draw_path_in_irrlicht(self._system, asset.center)
                draw_path_in_irrlicht(self._system, asset.left)
                draw_path_in_irrlicht(self._system, asset.right)


try:
    from wa_simulator.chrono.sensor import WAChronoSensorManager

    import pychrono.sensor as sens

    class WAChronoSensorVisualization(WAVisualization):
        """Chrono sensor visualization wrapper. Sets default values for a camera sensor

        Args:
            system (WAChronoSystem): holds information regarding the simulation and performs dynamic updates
            vehicle (WAChronoVehicle): vehicle that holds the Chrono vehicle
            vehicle_inputs (WAVehicleInputs): the vehicle inputs
            environment (WAEnvironment, optional): An environment with various world assets to visualize. Defaults to None (doesn't visualize anything).
            opponents (list, optional): Opponents present in the simulation. The camera will track :attr:`~vehicle` not any opponent.
            record (bool, optional): If set to true, images will be saved under record_filename. Defaults to False (doesn't save images).
            record_folder (str, optional): The folder to save images to. Defaults to "OUTPUT/".
        """

        def __init__(self, system: 'WAChronoSystem', vehicle: 'WAChronoVehicle', vehicle_inputs: 'WAVehicleInputs', environment: 'WAEnvironment' = None, opponents: list = [], record: bool = False, record_folder: str = "OUTPUT/"):
            self._render_steps = int(
                ceil(system.render_step_size / system.step_size))

            self._system = system
            self._vehicle_inputs = vehicle_inputs

            self._record = record
            self._record_folder = record_folder

            self._manager = WAChronoSensorManager(system)
            self._manager._manager.scene.AddPointLight(chrono.ChVectorF(0, 0, 100), chrono.ChVectorF(2, 2, 2), 5000)

            update_rate = 30.
            offset_pose = chrono.ChFrameD(chrono.ChVectorD(-8, 0, 2))
            image_width = 1280
            image_height = 720
            fov = 1.408
            cam = sens.ChCameraSensor(
                vehicle._vehicle.GetChassisBody(),              # body camera is attached to
                update_rate,            # update rate in Hz
                offset_pose,            # offset pose
                image_width,            # image width
                image_height,           # image height
                fov                    # camera's horizontal field of view
            )

            cam.PushFilter(sens.ChFilterVisualize(image_width, image_height))
            if self._record:
                cam.PushFilter(sens.ChFilterSave(self._record_folder))

            self._manager._manager.AddSensor(cam)

            if environment is not None:
                self.visualize(environment.get_assets())

        def synchronize(self, time: float):
            self._manager.synchronize(time)

        def advance(self, step: float):
            self._manager.advance(step)

        def is_ok(self):
            return True

        def visualize(self, assets, *args, **kwargs):
            pass
except:
    pass
