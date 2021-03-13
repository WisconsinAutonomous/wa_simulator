"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# WA Simulator
from wa_simulator.core import WAVector
from wa_simulator.visualization import WAVisualization
from wa_simulator.inputs import WAVehicleInputs

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


def create_sphere_in_irrlicht(system: 'WAChronoSystem', rgb=(1, 0, 0)) -> chrono.ChBodyEasySphere:
    """Create and add a sphere to the irrlicht visualization

    Args:
        system (WASystem): the system that manages the simulation
        rgb (tuple, optional): (red, green, blue). Defaults to (1, 0, 0) or red.

    Returns:
        chrono.ChBodyEasySphere: the sphere that was created
    """
    sphere = chrono.ChBodyEasySphere(0.25, 1000, True, False)
    sphere.SetBodyFixed(True)
    sphere.AddAsset(chrono.ChColorAsset(*rgb))
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
    """

    def __init__(self, system: 'WAChronoSystem', vehicle: 'WAChronoVehicle', vehicle_inputs: 'WAVehicleInputs'):
        self._render_steps = int(
            ceil(system.render_step_size / system.step_size))

        self._system = system
        self._vehicle_inputs = vehicle_inputs

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

    def visualize(self, path: 'WAPath', *args, **kwargs):
        draw_path_in_irrlicht(self._system, path)
