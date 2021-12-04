"""
Wisconsin Autonomous - https://wa.wisc.edu

Copyright (c) 2021 wa.wisc.edu
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

from abc import ABC, abstractmethod  # Abstract Base Class

# WA Simulator
from wa_simulator.base import WABase
from wa_simulator.core import WA_EARTH_RADIUS, WA_PI, WAVector
from wa_simulator.utils import _load_json, _check_field, _check_field_allowed_values, _WAStaticAttribute, get_wa_data_file

# Other Imports
import json
import numpy as np


def load_sensor_suite_from_json(manager: 'WASensorManager', filename: str):
    """Load a sensor suite from json

    Each loaded sensor will be added to the manager

    Args:
        manager (WASensorManager): The sensor manager to store all created objects in
        filename (str): The json specification file that describes the sensor suite
    """
    j = _load_json(filename)

    # Validate the json file
    _check_field(j, 'Type', value='Sensor')
    _check_field(j, 'Template', value='Sensor Suite')
    _check_field(j, 'Sensors', field_type=list)

    # Load the sensors
    for sensor in j['Sensors']:
        new_sensor = load_sensor_from_json(sensor, manager._system)
        manager.add_sensor(new_sensor)


def load_sensor_from_json(system: 'WASystem', filename: str, **kwargs) -> 'WASensor':
    """Load a sensor from json

    Args:
        system (WASystem): The system for the simulation
        filename (str): The json specification file that describes the sensor
        kwargs: Keyworded arguments. Must contain a 'vehicle' or 'body', not both.

    Returns:
        WASensor: The created sensor
    """
    j = _load_json(filename)

    # Validate the json file
    _check_field(j, 'Type', value='Sensor')
    _check_field(j, 'Template', allowed_values=['IMU', 'GPS'])

    # Check the template and create a sensor based off what it is
    if j['Template'] == 'IMU':
        sensor = WAIMUSensor(system, filename, **kwargs)
    elif j['Template'] == 'GPS':
        sensor = WAGPSSensor(system, filename, **kwargs)
    else:
        raise TypeError(f"{j['Template']} is not an implemented sensor type")

    return sensor


class WASensorManager(WABase):
    """Base class that manages sensors.

    Args:
        system (WASystem): The system for the simulation
        filename (str, optional): A json file to load a scene from. Defaults to None (does nothing).
    """

    # Global filenames for sensor suites
    _EGP_SENSOR_SUITE_FILE = "sensors/suites/ev_grand_prix.json"

    EGP_SENSOR_SUITE_FILE = _WAStaticAttribute('_EGP_SENSOR_SUITE_FILE', get_wa_data_file)

    def __init__(self, system: 'WASystem', filename: str = None):
        self._system = system

        self._sensors = []

        if filename is not None:
            load_sensor_suite_from_json(filename, self)

    def add_sensor(self, sensor: "WASensor"):
        """Add a sensor to the sensor manager"""
        self._sensors.append(sensor)

    def synchronize(self, time):
        """Synchronize each sensor at the specified time

        Args:
            time (float): the time at which the sensors are synchronized to
        """
        for sensor in self._sensors:
            sensor.synchronize(time)

    def advance(self, step):
        """Advance the state of each sensor by the specified time step

        Args:
            step (float): the step to update the sensor by
        """
        for sensor in self._sensors:
            sensor.advance(step)

    def is_ok(self) -> bool:
        for sensor in self._sensors:
            if not sensor.is_ok():
                return False
        return True


class WANoiseModel(ABC):
    """Base class for a noise model

    Very similar to ChNoiseModel (https://github.com/projectchrono/chrono/blob/feature/sensor/src/chrono_sensor/ChNoiseModel.h)
    Made because ChSensor currently _requires_ OptiX (NVIDIA proprietary software)
    """

    @abstractmethod
    def add_noise(data: list):
        """Add noise to the data

        Args:
            data (list): The data to add noise to
        """
        pass


class WANoNoiseModel(WANoiseModel):
    """Derived noise model. Does nothing"""

    def add_noise(data: list):
        """Do nothing"""
        pass


class WANormalDriftNoiseModel(WANoiseModel):
    """Derived noise model. Gaussian drifting noise with noncorrelated equal distributions

    Very similar to ChNormalDriftModel (https://github.com/projectchrono/chrono/blob/feature/sensor/src/chrono_sensor/ChNoiseModel.h)
    Made because ChSensor currently _requires_ OptiX (NVIDIA proprietary software)

    Args:
        p (dict): Model properties/parameters taken from a json specification file
    """

    def __init__(self, p: dict):
        # Validate properties
        _check_field(p, 'Noise Type', value='Normal Drift')
        _check_field(p, 'Update Rate', field_type=float)
        _check_field(p, 'Mean', field_type=list)
        _check_field(p, 'Standard Deviation', field_type=list)
        _check_field(p, 'Bias Drift', field_type=float)
        _check_field(p, 'Tau Drift', field_type=float)

        self._load_properties(p)

    def _load_properties(self, p: dict):
        """Private function that loads propeties and sets them to class variables

        Args:
            p (dict): Propeties dictionary
        """
        self._update_rate = p['Update Rate']
        self._mean = WAVector(p['Mean'])
        self._sigma = WAVector(p['Standard Deviation'])
        self._bias_drift = p['Bias Drift']
        self._tau_drift = p['Tau Drift']

        self._bias = WAVector()

    def add_noise(self, data: list):
        """Add noise to the data

        Args:
            data (list): The data to add noise to
        """

        def rand(element):
            return np.random.normal(getattr(self._mean, element, 0), getattr(self._sigma, element, 0))

        eta_a = WAVector([rand('x'), rand('y'), rand('z')])

        eta_b = WAVector()
        if self._tau_drift > 0 and self._bias_drift > 0:
            def rand(): return np.random.normal(0.0, self._drift_bias * np.sqrt(1.0 / (self._update_rate * self._tau_drift)))  # noqa
            eta_b = WAVector([rand(), rand(), rand()])

        self._bias += eta_b
        data += eta_a + self._bias


class WANormalNoiseModel(WANoiseModel):
    """Derived noise model. Gaussian drifting noise with noncorrelated equal distributions

    Very similar to ChNormalModel (https://github.com/projectchrono/chrono/blob/feature/sensor/src/chrono_sensor/ChNoiseModel.h)
    Made because ChSensor currently _requires_ OptiX (NVIDIA proprietary software)

    Args:
        p (dict): Model properties/parameters taken from a json specification file
    """

    def __init__(self, p: dict):
        # Validate properties
        _check_field(p, 'Noise Type', value='Normal')
        _check_field(p, 'Mean', field_type=list)
        _check_field(p, 'Standard Deviation', field_type=list)

        self._load_properties(p)

    def _load_properties(self, p: dict):
        """Private function that loads propeties and sets them to class variables

        Args:
            p (dict): Propeties dictionary
        """
        self._mean = WAVector(p['Mean'])
        self._sigma = WAVector(p['Standard Deviation'])

    def add_noise(self, data: list):
        """Add noise to the data

        Args:
            data (list): The data to add noise to
        """

        def rand(element):
            return np.random.normal(getattr(self._mean, element, 0), getattr(self._sigma, element, 0))

        data += WAVector([rand('x'), rand('y'), rand('z')])


class WASensor(WABase):
    """Base class for a sensor

    For the WASimulator, a sensor is a component that produces some sensor data. Each sensor is managed by a :class:`~WASensorManager`
    and will typically provide information for a vehicle or the surroundings. Common sensors used in autonomous vehicle
    applications: GPS, IMU, Camera, LiDAR. 

    Sensor implementations are some what limited to the underlying backend for the simulation. If Chrono is used, 
    Physics Based Rendering (PBR) sensors are available through the ray tracing engine `OptiX <https://developer.nvidia.com/optix>`_ 
    and `Chrono::Sensor <https://api.projectchrono.org/group__sensor__sensors.html>`_.

    Args:
        vehicle (WAVehicle): The vehicle to attach to. If not passed, body must be passed.
        body (WABody): The body to attach to. If not passed, vehicle must be passed.
    """

    def __init__(self, vehicle: 'WAVehicle', body: 'WABody'):
        if vehicle is not None and body is not None:
            raise ValueError(f"'vehicle' and 'body' are both set, but this is not allowed. Please only pass one.")
        elif vehicle is None and body is None:
            raise ValueError(f"'vehicle' and 'body' are both not set. Please set one.")

        if vehicle is not None:
            pass
        else:
            if not hasattr(body, 'position') or not isinstance(body.position, WAVector):
                raise ValueError(f"'body' must have a position attribute and it must be a 'WAVector'.")

    @abstractmethod
    def synchronize(self, time: float):
        pass

    @abstractmethod
    def advance(self, step: float):
        pass

    def is_ok(self) -> bool:
        return True

    @abstractmethod
    def get_data(self):
        """Get the sensor data

        Return types may vary. See the respective sensor for specifics.
        """
        pass


class WAIMUSensor(WASensor):
    """Derived sensor class that implements an IMU model

    IMU stands for Inertial Measurement Unit. They come in all shapes and sizes. Typically, an IMU is used to 
    measure position and orientation of whatever it is attached to. To do this, it is actually made up of more sensors,
    which when combined, produce a localizable reading. Common sub-sensors include Gyroscopes, Accelerometers, Altimeters and
    Magnetometer.

    This implementation combines three sensors to produce the expected output: Gyroscope, Accelerometer and Magnetometer. A good
    description of the underyling implementation can be found in `these slides <https://stanford.edu/class/ee267/lectures/lecture9.pdf>`_.

    Args:
        system (WASystem): The system for the simulation
        filename (str): a json specification file that describes an IMU sensor model
        vehicle (WAVehicle, optional): The vehicle to attach to. If not passed, body must be passed.
        body (WABody, optional): The body to attach to. If not passed, vehicle must be passed.
    """

    # Global filenames for imu sensors
    _SBG_IMU_SENSOR_FILE = "sensors/models/SBG_IMU.json"

    SBG_IMU_SENSOR_FILE = _WAStaticAttribute('_SBG_IMU_SENSOR_FILE', get_wa_data_file)

    def __init__(self, system: 'WASystem', filename: str, vehicle: 'WAVehicle' = None, body: 'WABody' = None):
        super().__init__(vehicle, body)

        if body is not None:
            raise NotImplementedError("Setting 'body' is currently not supported. Please pass a vehicle instead")

        self._vehicle = vehicle
        self._pos_dtdt = None
        self._rot = None 
        self._rot_dt = None 

        j = _load_json(filename)

        # Validate the json file
        _check_field(j, 'Type', value='Sensor')
        _check_field(j, 'Template', value='IMU')
        _check_field(j, 'Properties', field_type=dict)

        p = j['Properties']
        _check_field(p, 'Update Rate', field_type=int)
        _check_field(p, 'Noise Model', field_type=dict, optional=True)

        if 'Noise Model' in p:
            _check_field(p['Noise Model'], 'Noise Type',
                         allowed_values=["Normal", "Normal Drift"])

        self._load_properties(p)

        self._acc = WAVector()
        self._omega = WAVector()
        self._orientation = WAVector()

    def _load_properties(self, p: dict):
        """Private function that loads properties and sets them to class variables

        Args:
            p (dict): Properties dictionary
        """
        self._update_rate = p['Update Rate']

        self._noise_model = WANoNoiseModel()
        if 'Noise Model' in p:
            n = p['Noise Model']

            if n['Noise Type'] == 'Normal Drift':
                self._noise_model = WANormalDriftNoiseModel(n)
            elif n['Noise Type'] == 'Normal':
                self._noise_model = WANormalNoiseModel(n)
            else:
                raise TypeError(
                    f"{p['Noise Type']} is not an implemented model type")

    def synchronize(self, time):
        """Synchronize the sensor at the specified time

        Args:
            time (float): the time at which the sensors are synchronized to
        """
        self._noise_model.add_noise(self._acc)  # Acceleration (accelerometer)
        # Angular velocity (gyroscope)
        self._noise_model.add_noise(self._omega)
        # self.noise_model.add_noise(self.orientation)  # Orientation ("Magnometer") # noqa

    def advance(self, step):
        """Advance the state of the sensor by the specified time step

        Args:
            step (float): the step to update the sensor by
        """
        self._pos_dtdt = self._vehicle.get_pos_dtdt()
        self._rot = self._vehicle.get_rot()
        self._rot_dt = self._vehicle.get_rot_dt()

    def get_data(self):
        """Get the sensor data

        Returns:
            (WAVector, WAQuaternion, WAQuaternion): Tuple in the form of (acceleration, angular_velocity, orientation)
        """
        if self._pos_dtdt is None and self._rot_dt is None and self._rot is None:
            return None
        return self._pos_dtdt, self._rot_dt, self._rot


class WAGPSSensor(WASensor):
    """Derived sensor class that implements an GPS model

    GPS stands for Global Positioning System. GPS's are everyday sensors you can find in your computer, watch, phone, etc.
    They essentially ping satilites orbiting earth for positional information. This information, in real life, is not very
    precise. IMU's and GPS's are commonly "fused" together to achieve highly accurate and reliable position information.

    Args:
        system (WASystem): The system for the simulation
        filename (str): a json specification file that describes an GPS sensor model
        vehicle (WAVehicle, optional): The vehicle to attach to. If not passed, body must be passed.
        body (WABody, optional): The body to attach to. If not passed, vehicle must be passed.
    """

    # Global filenames for gps sensors
    _SBG_GPS_SENSOR_FILE = "sensors/models/SBG_GPS.json"

    SBG_GPS_SENSOR_FILE = _WAStaticAttribute('_SBG_GPS_SENSOR_FILE', get_wa_data_file)

    def __init__(self, system: 'WASystem', filename: str, vehicle: 'WAVehicle' = None, body: 'WABody' = None):
        super().__init__(vehicle, body)

        if body is not None:
            raise NotImplementedError("Setting 'body' is currently not supported. Please pass a vehicle instead")

        self._vehicle = vehicle
        self._coord = None

        j = _load_json(filename)

        # Validate the json file
        _check_field(j, 'Type', value='Sensor')
        _check_field(j, 'Template', value='GPS')
        _check_field(j, 'Properties', field_type=dict)

        p = j['Properties']
        _check_field(p, 'Update Rate', field_type=int)
        _check_field(p, 'GPS Reference', field_type=list)
        _check_field(p, 'Noise Model', field_type=dict, optional=True)

        if 'Noise Model' in p:
            _check_field(p['Noise Model'], 'Noise Type',
                         allowed_values=["Normal", "Normal Drift"])

        self._load_properties(p)

    def _load_properties(self, p: dict):
        """Private function that loads properties and sets them to class variables

        Args:
            p (dict): Properties dictionary
        """
        self._update_rate = p['Update Rate']
        self._reference = WAVector(p['GPS Reference'])

        self._noise_model = WANoNoiseModel()
        if 'Noise Model' in p:
            n = p['Noise Model']

            if n['Noise Type'] == 'Normal Drift':
                self._noise_model = WANormalDriftNoiseModel(n)
            elif n['Noise Type'] == 'Normal':
                self._noise_model = WANormalNoiseModel(n)
            else:
                raise TypeError(
                    f"{p['Noise Type']} is not an implemented model type")

        self._pos = WAVector()

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
        self._pos = self._vehicle.get_pos()
        self._noise_model.add_noise(self._pos)
        self._coord = WAGPSSensor.cartesian_to_gps(self._pos, self._reference)

    def get_data(self):
        """Get the sensor data

        Returns:
            WAVector: The coordinate location of the vehicle in the form of [longitude, latitude, altitude]
        """
        return self._coord

    @staticmethod
    def cartesian_to_gps(coords: WAVector, ref: WAVector):
        """Convert a point from cartesian to gps

        Args:
          coords(WAVector): The coordinate to convert
          ref(WAVector): The "origin" or reference point

        Returns:
          WAVector: The coordinate in the form of[longitude, latitude, altitude]
        """
        lat = (coords.y / WA_EARTH_RADIUS) * 180.0 / WA_PI + ref.y
        lon = (coords.x / (WA_EARTH_RADIUS * np.cos(lat * WA_PI / 180.0))) * 180.0 / WA_PI + ref.x  # noqa
        alt = coords.z + ref.z

        lon = lon + 360.0 if lon < -180.0 else lon - 360.0 if lon > 180.0 else lon

        return WAVector([lon, lat, alt])

    @staticmethod
    def gps_to_cartesian(coords: WAVector, ref: WAVector):
        """Convert a gps coordinate to cartesian given some reference

        Args:
          coords(WAVector): The coordinate to convert
          ref(WAVector): The "origin" or reference point

        Returns:
          WAVector: The x, y, z point in cartesian
        """
        lon = coords.x
        lat = coords.y
        alt = coords.z

        x = ((lon - ref.x) * WA_PI / 180.0) * (WA_EARTH_RADIUS * np.cos(lat * WA_PI / 180.0))  # noqa
        y = ((lat - ref.y) * WA_PI / 180.0) * WA_EARTH_RADIUS
        z = alt - ref.z

        return WAVector([x, y, z])
