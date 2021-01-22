"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# WA Simulator
from wa_simulator.vector import WAVector
from wa_simulator.visualization import WAVisualization

# Chrono specific imports
import pychrono as chrono
import pychrono.vehicle as veh
import pychrono.irrlicht as irr

# Other imports
import numpy as np
from math import ceil


def draw_path_in_irrlicht(path, sys):
    """Draw a path object in irrlicht

    Args:
        path (WAPath): WA path object to visualize in irrlicht
        sys (WASystem): system that manages the simulation
    """
    ch_points = chrono.vector_ChVectorD()
    for p in np.column_stack((path.x, path.y)):
        ch_points.push_back(chrono.ChVectorD(p[0], p[1], 0.5))
    curve = chrono.ChBezierCurve(ch_points)

    road = sys.system.NewBody()
    road.SetBodyFixed(True)
    sys.system.AddBody(road)

    num_points = len(path.x)
    path_asset = chrono.ChLineShape()
    path_asset.SetLineGeometry(chrono.ChLineBezier(curve))
    path_asset.SetColor(chrono.ChColor(0, 0.8, 0))
    path_asset.SetNumRenderPoints(max(2 * num_points, 400))
    road.AddAsset(path_asset)


def create_sphere_in_irrlicht(system, rgb=(1, 0, 0)):
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
    system.system.Add(sphere)

    return sphere


def update_position_of_sphere(sphere, pos):
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
        vehicle (WAChronoVehicle): vehicle that holds the Chrono vehicle
        system (WAChronoSystem): holds information regarding the simulation and performs dynamic updates

    Attributes:
        render_steps (int): steps between which the visualization should update
        system (WAChronoSystem): system used to grab certain parameters of the simulation
        app (ChVehicleIrrApp): The vehicle irrlicht app that displays the 3D rendering
    """

    def __init__(self, vehicle, system):
        self.render_steps = int(
            ceil(system.render_step_size / system.step_size))

        self.system = system

        self.app = veh.ChVehicleIrrApp(vehicle.vehicle)
        self.app.SetHUDLocation(500, 20)
        self.app.SetSkyBox()
        self.app.AddTypicalLogo()
        self.app.AddTypicalLights(
            irr.vector3df(-150.0, -150.0, 200.0),
            irr.vector3df(-150.0, 150.0, 200.0),
            100,
            100,
        )
        self.app.AddTypicalLights(
            irr.vector3df(150.0, -150.0, 200.0),
            irr.vector3df(150.0, 150.0, 200.0),
            100,
            100,
        )
        self.app.SetChaseCamera(chrono.ChVectorD(0.0, 0.0, 1.75), 6.0, 0.5)
        self.app.SetTimestep(system.step_size)

        self.app.AssetBindAll()
        self.app.AssetUpdateAll()

    def advance(self, step):
        """Advance the state of the visualization by the specified step

        Will update the render only if the simulation step is a multiple of render steps

        Args:
            step (double): step size to update the visualization by
        """
        if self.system.get_step_number() % self.render_steps == 0:
            self.app.BeginScene(True, True, irr.SColor(255, 140, 161, 192))
            self.app.DrawAll()
            self.app.EndScene()

        self.app.Advance(step)

    def synchronize(self, time, vehicle_inputs):
        """Synchronize the irrlicht app with the vehicle inputs at the passed time

        Args:
            time (double): time to synchronize the simulation to
            vehicle_inputs (WAVehicleInputs): the vehicle inputs
        """
        d = veh.Inputs()
        d.m_steering = vehicle_inputs.steering
        d.m_throttle = vehicle_inputs.throttle
        d.m_braking = vehicle_inputs.braking
        vehicle_inputs = d

        self.app.Synchronize("", vehicle_inputs)

    def is_ok(self):
        """Checks if the irrlicht rending window is still alive

        Returns:
            bool: whether the simulation is still alive
        """
        return self.app.GetDevice().run()
