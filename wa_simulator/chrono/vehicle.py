"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# WA Simulator
from wa_simulator.vehicle import WAVehicle

# Chrono specific imports
import pychrono as chrono
import pychrono.vehicle as veh


def ReadVehicleModelFile(filename):
    """Read a json specification file to get additional file names to be loaded into ChVehicle classes

    Args:
        filename (str): the json specification file with Vehicle, Powertrain and Tire input models

    Returns:
        tuple: returns each json specification file for the vehicle, powertrain and tire
    """
    import json

    full_filename = veh.GetDataFile(filename)

    with open(full_filename) as f:
        j = json.load(f)

    if "Vehicle" not in j:
        print("'Vehicle' not present in the passed json file.")
        exit()
    vehicle_filename = veh.GetDataFile(j["Vehicle"]["Input File"])

    if "Powertrain" not in j:
        print("'Powertrain' not present in the passed json file.")
        exit()
    powertrain_filename = veh.GetDataFile(j["Powertrain"]["Input File"])

    if "Tire" not in j:
        print("'Tire' not present in the passed json file.")
        exit()
    tire_filename = veh.GetDataFile(j["Tire"]["Input File"])

    return vehicle_filename, powertrain_filename, tire_filename


def CreateTireFromJSON(tire_filename):
    """Creates a tire from a tire file

    Args:
        tire_filename (str): the tire json specification file

    Returns:
        ChTire: the created tire
    """
    import json

    with open(tire_filename) as f:
        j = json.load(f)

    if "Type" not in j:
        print("'Type' not present in the passed json file.")
        exit()

    if j["Type"] != "Tire":
        print("Passed json file is not a tire file.")
        exit()

    if "Template" not in j:
        print("'Template' not present in the passed json file.")
        exit()

    tire_type = j["Template"]
    if tire_type == "TMeasyTire":
        return veh.TMeasyTire(tire_filename)
    elif tire_type == "RigidTire":
        return veh.RigidTire(tire_filename)
    else:
        print(f"'{tire_type}' not a recognized tire type.")
        exit()


class WAChronoVehicle(WAVehicle):
    """Chrono vehicle wrapper

    Args:
        filename (str): json file specification file
        system (WAChronoSystem): the system used to run the simulation
        env (WAEnvironment): the environment with a terrain
        initLoc (chrono.ChVectorD, optional): the inital location of the vehicle. Defaults to chrono.ChVectorD(0, 0, 0.5).
        initRot (chrono.ChQuaternionD, optional): the initial orientation of the vehicle. Defaults to chrono.ChQuaternionD(1, 0, 0, 0).

    Attributes:
        vehicle (ChVehicle): a chrono vehicle that this class essentially wraps
        terrain (ChTerrain): a terrain that the vehicle interacts with
    """

    # Global filenames for vehicle models
    GO_KART_MODEL_FILE = "GoKart/GoKart.json"
    IAC_VEH_MODEL_FILE = "IAC/IAC.json"

    def __init__(
        self,
        filename,
        system,
        env,
        initLoc=chrono.ChVectorD(0, 0, 0.5),
        initRot=chrono.ChQuaternionD(1, 0, 0, 0),
    ):
        super().__init__("vehicles/GoKart/GoKart_KinematicBicycle.json")

        # Get the filenames
        vehicle_file, powertrain_file, tire_file = ReadVehicleModelFile(
            filename)

        # Create the vehicle
        vehicle = veh.WheeledVehicle(system.system, vehicle_file)

        # Initialize the vehicle
        vehicle.Initialize(chrono.ChCoordsysD(initLoc, initRot))

        # Set the visualization components for the vehicle
        vehicle.SetChassisVisualizationType(veh.VisualizationType_PRIMITIVES)
        vehicle.SetSuspensionVisualizationType(
            veh.VisualizationType_PRIMITIVES)
        vehicle.SetSteeringVisualizationType(veh.VisualizationType_PRIMITIVES)
        vehicle.SetWheelVisualizationType(veh.VisualizationType_NONE)

        # Create the powertrain
        # Assumes a SimplePowertrain
        powertrain = veh.SimplePowertrain(powertrain_file)
        vehicle.InitializePowertrain(powertrain)

        # Create and initialize the tires
        for axle in vehicle.GetAxles():
            tireL = CreateTireFromJSON(tire_file)
            vehicle.InitializeTire(
                tireL, axle.m_wheels[0], veh.VisualizationType_PRIMITIVES)
            tireR = CreateTireFromJSON(tire_file)
            vehicle.InitializeTire(
                tireR, axle.m_wheels[1], veh.VisualizationType_PRIMITIVES)

        self.vehicle = vehicle
        self.terrain = env.terrain.terrain

    def advance(self, step):
        """Perform a dynamics update

        Args:
            step (double): time step to update the vehicle by
        """
        self.vehicle.Advance(step)

    def synchronize(self, time, vehicle_inputs):
        """Synchronize the vehicle with the vehicle inputs at the passed time

        Args:
            time (double): time to synchronize the simulation to
            vehicle_inputs (WAVehicleInputs): the vehicle inputs
        """
        if not isinstance(self.terrain, veh.ChTerrain):
            raise TypeError("Synchronize: Terrain has not been set.")

        d = veh.Inputs()
        d.m_steering = vehicle_inputs.steering
        d.m_throttle = vehicle_inputs.throttle
        d.m_braking = vehicle_inputs.braking
        vehicle_inputs = d

        self.vehicle.Synchronize(time, vehicle_inputs, self.terrain)

    def get_simple_state(self):
        """Get a simple state representation of the vehicle.

        Returns:
            tuple: (x position, y position, yaw about the Z, speed)
        """
        pos = self.vehicle.GetVehiclePos()
        return (
            pos.x,
            pos.y,
            self.vehicle.GetVehicleRot().Q_to_Euler123().z,
            self.vehicle.GetVehicleSpeed(),
        )
