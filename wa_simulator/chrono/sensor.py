"""
Wisconsin Autonomous - https://wa.wisc.edu

Copyright (c) 2021 wa.wisc.edu
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# WA Simulator
from wa_simulator.utils import _check_type, _load_json, _check_field, get_wa_data_file, _WAStaticAttribute
from wa_simulator.sensor import WASensorManager, WASensor, load_sensor_from_json
from wa_simulator.chrono.vehicle import WAChronoVehicle
from wa_simulator.chrono.utils import ChVector_from_list, ChFrame_from_json, get_chrono_data_file, WAVector_to_ChVector
from wa_simulator.chrono.system import WAChronoSystem

# Chrono specific imports
import pychrono as chrono

try:
    import pychrono.sensor as sens
    missing_chrono_sensor = False
except ImportError:
    missing_chrono_sensor = True

    def sens_import_error(function_name: str):
        """Helper function that prints out if a function in this class is used when Chrono::Sensor isn't available for import"""
        msg = f"{function_name}: Requires Chrono::Sensor and was not found. Chrono::Sensor requires building Chrono from source. Consult Aaron Young (aryoung5@wisc.edu) if you have questions."
        raise RuntimeError(msg)


def load_chrono_sensor_scene_from_json(manager: "WAChronoSensorManager", filename: str):
    """Load a chrono sensor scene from a json specification file. A scene may consist of "World" attributes (i.e. lights) or sensors

    Args:
        manager (WASensorManager): The sensor manager to edit the scene of
        filename (str): The json specification file describing the scene
    """
    if missing_chrono_sensor:
        sens_import_error('load_chrono_sensor_scene_from_json')

    j = _load_json(filename)

    # Validate the json file
    _check_field(j, 'Type', value='Sensor')
    _check_field(j, 'Template', value='Chrono Sensor Scene')
    _check_field(j, 'World', field_type=dict, optional=True)
    _check_field(j, 'Sensors', field_type=list, optional=True)
    _check_field(j, 'Objects', field_type=list, optional=True)

    if 'World' in j:
        w = j['World']

        _check_field(w, 'Point Lights', field_type=list)

        # Create the point lights
        # NOTE: Might be optional in the future
        for p in w['Point Lights']:
            _check_field(p, 'Position', field_type=list)
            _check_field(p, 'Color', field_type=list)
            _check_field(p, 'Maximum Range', field_type=float)

            pos = ChVector_from_list(p['Position'], chrono.ChVectorF)
            color = ChVector_from_list(p['Color'], chrono.ChVectorF)
            max_range = p['Maximum Range']

            manager._manager.scene.AddPointLight(pos, color, max_range)

    if 'Sensors' in j:
        s = j['Sensors']

        for sensor in s:
            new_sensor = load_chrono_sensor_from_json(manager._system, sensor)
            manager.add_sensor(new_sensor)


def load_chrono_sensor_from_json(system: 'WAChronoSystem', filename: str, **kwargs) -> 'WAChronoSensor':
    """Load a chrono sensor from json

    If the passed json file isn't a chrono type, it will call the correct method.

    Args:
        system (WAChronoSystem): The system for the simulation
        filename (str): The json specification file that describes the sensor

    Returns:
            WAChronoSensor: The created sensor
    """
    if missing_chrono_sensor:
        sens_import_error('load_chrono_sensor_from_json')

    # Check if the file can be found in the chrono portion of the data folder
    try:
        j = _load_json(filename)
    except FileNotFoundError:
        # File is not chrono specific, try that now
        j = _load_json(get_wa_data_file(filename))
        return load_sensor_from_json(system, filename, **kwargs)

    return WAChronoSensor(system, filename, **kwargs)


class WAChronoSensorManager(WASensorManager):
    """Derived SensorManager class that essentially wraps a ChSensorManager. Used to maintain sensors.

    Args:
        system (WAChronoSystem): The system for the simulation
        vehicle (WAVehicle): The vehicle each sensor is attached to
        filename (str): A json file to load a scene from. Defaults to None (does nothing).
    """

    # Global filenames for environment models
    _EGP_SENSOR_SCENE_FILE = "sensors/scenes/ev_grand_prix.json"

    EGP_SENSOR_SCENE_FILE = _WAStaticAttribute('_EGP_SENSOR_SCENE_FILE', chrono.GetChronoDataFile)

    def __init__(self, system: 'WAChronoSystem', filename: str = None):
        if missing_chrono_sensor:
            sens_import_error('WAChronoSensorManager.__init__')

        _check_type(system, WAChronoSystem, 'system', 'WAChronoSensorManager.__init__')  # noqa

        super().__init__(system)

        self._manager = sens.ChSensorManager(system._system)

        if filename is not None:
            load_chrono_sensor_scene_from_json(self, filename)

    def add_sensor(self, sensor: "WAChronoSensor"):
        """Add a sensor to the sensor manager"""
        if isinstance(sensor, WAChronoSensor):
            self._manager.AddSensor(sensor._sensor)
        elif isinstance(sensor, WASensor):
            super().add_sensor(sensor)
        else:
            raise TypeError(
                f"WAChronoSensorManager.add_sensor: sensor has unknown type '{type(sensor)}'. Must be 'WAChronoSensor' or 'WASensor.")

    def advance(self, step):
        """Advance the state of the sensor by the specified time step

        Args:
            step(float): the step to update the sensor by
        """
        self._manager.Update()

        super().advance(step)


class WAChronoSensor(WASensor):
    """Derived Sensor class that is still abstract that essentially wraps a ChSensor.

    A ChSensor has to be attached to a body that's present in the Chrono world. That body can then be moved
    which then moves the ChSensor. If a vehicle is passed, the sensor is automatically attached to the chassis
    body with some offset. If a vehicle is not passed, a :class:`~WABody` must be passed and the sensor
    will be attached to that object. If both are passed, an exception is raised.

    If body is passed, it must have one attribute: position.

    Args:
        system (WAChronoSystem): The system for the simulation
        filename (str): The json file that describes this sensor
        vehicle (WAChronoVehicle, optional): The vehicle to attach to. If not passed, body must be passed.
        body (WABody, optional): The body to attach to. If not passed, vehicle must be passed.
    """

    # Global filenames for various sensors
    _MONO_CAM_SENSOR_FILE = "sensors/models/generic_monocamera.json"
    _LDMRS_LIDAR_SENSOR_FILE = "sensors/models/ldmrs.json"

    MONO_CAM_SENSOR_FILE = _WAStaticAttribute('_MONO_CAM_SENSOR_FILE', get_chrono_data_file)
    LDMRS_LIDAR_SENSOR_FILE = _WAStaticAttribute('_LDMRS_LIDAR_SENSOR_FILE', get_chrono_data_file)

    def __init__(self, system: 'WAChronoSystem', filename: str, vehicle: 'WAChronoVehicle' = None, body: 'WABody' = None):
        if missing_chrono_sensor:
            sens_import_error('WAChronoSensor.__init__')

        super().__init__(vehicle, body)

        j = _load_json(filename)

        # Validate the json file
        _check_field(j, 'Type', value='Sensor')
        _check_field(j, 'Template', allowed_values=['Camera', 'Lidar', 'IMU', 'GPS'])  # noqa
        _check_field(j, 'Offset Pose', field_type=dict)

        offset_pose = ChFrame_from_json(j['Offset Pose'])

        if vehicle is not None:
            body = vehicle._vehicle.GetChassisBody()
        else:
            asset = body
            body = chrono.ChBody()
            body.SetPos(WAVector_to_ChVector(asset.position))
            body.SetBodyFixed(True)
            system._system.AddBody(body)

            # Create the chrono sensor through the Sensor chrono class
        self._sensor = sens.Sensor.CreateFromJSON(filename, body, offset_pose)  # noqa

    def synchronize(self, time):
        """Synchronize the sensor at the specified time

        Args:
            time (float): the time at which the sensors are synchronized to
        """
        pass

    def advance(self, step):
        """Advance the state of the sensor by the specified time step

        Args:
            step (float): the step to update the sensor by
        """
        pass

    def get_data(self):
        """Get the sensor data

        Returns:
            np.ndarray: The sensor data. Type depends on the actual sensor
        """
        name = self._sensor.GetName().lower()
        if 'camera' in name:
            buff = self._sensor.GetMostRecentRGBA8Buffer()
            return buff.GetRGBA8Data()
        if 'lidar' in name:
            buff = self._sensor.GetMostRecentXYZIBuffer()
            return buff.GetXYZIData()
        else:
            raise TypeError(
                f"WAChronoSensorManager.get_data: can't determine sensor type from name: '{name}'.")
