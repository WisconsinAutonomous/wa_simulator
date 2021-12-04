"""
Wisconsin Autonomous - https://wa.wisc.edu

Copyright (c) 2021 wa.wisc.edu
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# WA Simulator
from wa_simulator.vehicle import WAVehicle
from wa_simulator.core import WAVector, WAQuaternion
from wa_simulator.utils import _check_field, _load_json, get_wa_data_file, _WAStaticAttribute
from wa_simulator.chrono.utils import ChVector_to_WAVector, ChQuaternion_to_WAQuaternion, WAVector_to_ChVector, WAQuaternion_to_ChQuaternion, get_chrono_data_file, get_chrono_vehicle_data_file

# Chrono specific imports
import pychrono as chrono
import pychrono.vehicle as veh


def read_vehicle_model_file(filename: str) -> tuple:
    """Read a json specification file to get additional file names to be loaded into ChVehicle classes

    Will find the vehicle, powertrain and tire input files. The input files are other json files that are
    readable by the Chrono simulator to be used to create bodies attached to the vehicle.

    Args:
        filename (str): the json specification file with Vehicle, Powertrain and Tire input models

    Returns:
        tuple: returns each json specification file for the vehicle, powertrain and tire
    """
    j = _load_json(filename)

    # Validate json file
    _check_field(j, "Vehicle", field_type=dict)
    _check_field(j, "Powertrain", field_type=dict)
    _check_field(j, "Tire", field_type=dict)

    _check_field(j["Vehicle"], "Input File", field_type=str)
    _check_field(j["Powertrain"], "Input File", field_type=str)
    _check_field(j["Tire"], "Input File", field_type=str)

    # Extract the actual files
    vehicle_filename = veh.GetDataFile(j["Vehicle"]["Input File"])
    powertrain_filename = veh.GetDataFile(j["Powertrain"]["Input File"])
    tire_filename = veh.GetDataFile(j["Tire"]["Input File"])

    return vehicle_filename, powertrain_filename, tire_filename


def create_tire_from_json(tire_filename: str) -> veh.ChTire:
    """Creates a ChTire from a tire file

    .. info:
        Currently, only TMeasyTires and RigidTires are supported

    Args:
        tire_filename (str): the tire json specification file

    Returns:
        ChTire: the created tire

    Raises:
        TypeError: If the tire type is not recognized
    """
    j = _load_json(tire_filename)

    # Valide json file
    _check_field(j, "Type", value="Tire")
    _check_field(j, "Template", allowed_values=[
                 "TMeasyTire", "RigidTire", "Pac02Tire"])

    tire_type = j["Template"]
    if tire_type == "TMeasyTire":
        return veh.TMeasyTire(tire_filename)
    elif tire_type == "RigidTire":
        return veh.RigidTire(tire_filename)
    elif tire_type == "Pac02Tire":
        return veh.Pac02Tire(tire_filename)
    else:
        raise TypeError(f"'{tire_type} not a recognized tire type")


class WAChronoVehicle(WAVehicle):
    """Chrono vehicle wrapper

    Args:
        system (WAChronoSystem): the system used to run the simulation
        env (WAEnvironment): the environment with a terrain
        vehicle_inputs (WAVehicleInputs): the vehicle inputs
        filename (str): json file specification file
        init_loc (WAVector, optional): the inital location of the vehicle. Defaults to WAVector([0, 0, 0.5]).
        init_rot (WAQuaternion, optional): the initial orientation of the vehicle. Defaults to WAQuaternion([1, 0, 0, 0]).
        init_speed (WAVector, optional): the initial forward speed of the vehicle. Defaults to 0.0.
    """

    # Global filenames for vehicle models
    _GO_KART_MODEL_FILE = "GoKart/GoKart.json"

    GO_KART_MODEL_FILE = _WAStaticAttribute(
        '_GO_KART_MODEL_FILE', get_chrono_vehicle_data_file)

    def __init__(self, system: 'WAChronoSystem', vehicle_inputs: 'WAVehicleInputs', env: 'WAEnvironment', filename: str, init_loc: WAVector = WAVector([0, 0, 0.5]), init_rot: WAQuaternion = WAQuaternion([1, 0, 0, 0]), init_speed: float = 0.0):
        super().__init__(system, vehicle_inputs, get_wa_data_file(
            "vehicles/GoKart/GoKart_KinematicBicycle.json"))

        # Get the filenames
        vehicle_file, powertrain_file, tire_file = read_vehicle_model_file(
            filename)

        # Create the vehicle
        vehicle = veh.WheeledVehicle(system._system, vehicle_file)

        # Initialize the vehicle
        init_loc = WAVector_to_ChVector(init_loc)
        init_rot = WAQuaternion_to_ChQuaternion(init_rot)
        vehicle.Initialize(chrono.ChCoordsysD(init_loc, init_rot), init_speed)

        # Set the visualization components for the vehicle
        vehicle.SetChassisVisualizationType(veh.VisualizationType_MESH)
        vehicle.SetSuspensionVisualizationType(veh.VisualizationType_NONE)
        vehicle.SetSteeringVisualizationType(veh.VisualizationType_NONE)
        vehicle.SetWheelVisualizationType(veh.VisualizationType_MESH)

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

        self._vehicle = vehicle
        self._terrain = env._terrain

    def synchronize(self, time: float):
        d = veh.Inputs()
        d.m_steering = self._vehicle_inputs.steering
        d.m_throttle = self._vehicle_inputs.throttle
        d.m_braking = self._vehicle_inputs.braking

        self._vehicle.Synchronize(time, d, self._terrain)

    def advance(self, step: float):
        self._vehicle.Advance(step)

    def get_pos(self) -> WAVector:
        return ChVector_to_WAVector(self._vehicle.GetVehiclePos())

    def get_rot(self) -> WAQuaternion:
        return ChQuaternion_to_WAQuaternion(self._vehicle.GetVehicleRot())

    def get_pos_dt(self) -> WAVector:
        vel = self._vehicle.GetChassisBody().PointSpeedLocalToParent(
            self._vehicle.GetChassis().GetLocalDriverCoordsys().pos)
        vel = self._vehicle.GetChassisBody().GetRot().Rotate(vel)
        return ChVector_to_WAVector(vel)

    def get_rot_dt(self) -> WAQuaternion:
        return ChVector_to_WAVector(self._vehicle.GetChassisBody().GetWvel_loc())

    def get_pos_dtdt(self) -> WAVector:
        acc = self._vehicle.GetChassisBody().PointAccelerationLocalToParent(
            self._vehicle.GetChassis().GetLocalDriverCoordsys().pos)
        acc = self._vehicle.GetChassisBody().GetRot().Rotate(acc) - \
            self._vehicle.GetSystem().Get_G_acc()
        return ChVector_to_WAVector(acc)

    def get_rot_dtdt(self) -> WAQuaternion:
        return ChVector_to_WAVector(self._vehicle.GetChassisBody().GetWacc_loc())
