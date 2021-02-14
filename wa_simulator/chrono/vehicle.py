"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# WA Simulator
from wa_simulator.utils import check_field, load_json
from wa_simulator.vehicle import WAVehicle
from wa_simulator.chrono.utils import ChVector_to_WAVector, ChQuaternion_to_WAQuaternion

# Chrono specific imports
import pychrono as chrono
import pychrono.vehicle as veh


def read_vehicle_model_file(filename):
    """Read a json specification file to get additional file names to be loaded into ChVehicle classes

    Args:
        filename (str): the json specification file with Vehicle, Powertrain and Tire input models

    Returns:
        tuple: returns each json specification file for the vehicle, powertrain and tire
    """
    j = load_json(veh.GetDataFile(filename))

    # Validate json file
    check_field(j, "Vehicle", field_type=dict)
    check_field(j, "Powertrain", field_type=dict)
    check_field(j, "Tire", field_type=dict)

    check_field(j["Vehicle"], "Input File", field_type=str)
    check_field(j["Powertrain"], "Input File", field_type=str)
    check_field(j["Tire"], "Input File", field_type=str)

    # Extract the actual files
    vehicle_filename = veh.GetDataFile(j["Vehicle"]["Input File"])
    powertrain_filename = veh.GetDataFile(j["Powertrain"]["Input File"])
    tire_filename = veh.GetDataFile(j["Tire"]["Input File"])

    return vehicle_filename, powertrain_filename, tire_filename


def create_tire_from_json(tire_filename):
    """Creates a tire from a tire file

    Args:
        tire_filename (str): the tire json specification file

    Returns:
        ChTire: the created tire
    """
    j = load_json(tire_filename)

    # Valide json file
    check_field(j, "Type", value="Tire")
    check_field(j, "Template", allowed_values=["TMeasyTire", "RigidTire"])

    tire_type = j["Template"]
    if tire_type == "TMeasyTire":
        return veh.TMeasyTire(tire_filename)
    elif tire_type == "RigidTire":
        return veh.RigidTire(tire_filename)
    else:
        raise TypeError(f"'{tire_type} not a recognized tire type")


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
        vehicle_file, powertrain_file, tire_file = read_vehicle_model_file(
            filename)

        # Create the vehicle
        vehicle = veh.WheeledVehicle(system.system, vehicle_file)

        # Initialize the vehicle
        vehicle.Initialize(chrono.ChCoordsysD(initLoc, initRot))

        # Set the visualization components for the vehicle
        vehicle.SetChassisVisualizationType(veh.VisualizationType_PRIMITIVES)
        vehicle.SetSuspensionVisualizationType(veh.VisualizationType_NONE)
        vehicle.SetSteeringVisualizationType(veh.VisualizationType_NONE)
        vehicle.SetWheelVisualizationType(veh.VisualizationType_NONE)

        # Create the powertrain
        # Assumes a SimplePowertrain
        powertrain = veh.SimplePowertrain(powertrain_file)
        vehicle.InitializePowertrain(powertrain)

        # Create and initialize the tires
        for axle in vehicle.GetAxles():
            tireL = create_tire_from_json(tire_file)
            vehicle.InitializeTire(
                tireL, axle.m_wheels[0], veh.VisualizationType_MESH)
            tireR = create_tire_from_json(tire_file)
            vehicle.InitializeTire(
                tireR, axle.m_wheels[1], veh.VisualizationType_MESH)

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

    def _get_acceleration(self):
        """Get the acceleration of the vehicle

        Really shouldn't be used by a controller. Made for sensor related calculations

        Returns:
            WAVector: The acceleration where X is forward, Z is up and Y is left (ISO standard)
        """

        acc = self.vehicle.GetChassisBody().PointAccelerationLocalToParent(
            self.vehicle.GetChassis().GetLocalDriverCoordsys().pos)
        acc = self.vehicle.GetChassisBody().GetRot().Rotate(acc) - \
            self.vehicle.GetSystem().Get_G_acc()
        return ChVector_to_WAVector(acc)

    def _get_angular_velocity(self):
        """Get the angular velocity of the vehicle

        Really shouldn't be used by a controller. Made for sensor related calculations

        Returns:
            WAVector: The angular velocity
        """
        return ChVector_to_WAVector(self.vehicle.GetChassisBody().GetWvel_loc())

    def _get_position(self):
        """Get the position of the vehicle

        Really shouldn't be used by a controller. Made for sensor related calculations

        Returns:
            WAVector: The position of the vehicle
        """
        return ChVector_to_WAVector(self.vehicle.GetVehiclePos())

    def _get_orientation(self):
        """Get the orientation of the vehicle

        Really shouldn't be used by a controller. Made for sensor related calculations

        Returns:
            WAVector: The orientation of the vehicle
        """
        return ChQuaternion_to_WAQuaternion(self.vehicle.GetVehicleRot())
