"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

from abc import ABC, abstractmethod  # Abstract Base Class

# WA Simulator
from wa_simulator.system import WASystem
from wa_simulator.core import WAVector
from wa_simulator.utils import load_json, check_field, check_field_allowed_values, get_wa_data_file
from wa_simulator.vehicle import WAVehicle
from wa_simulator.constants import WA_EARTH_RADIUS, WA_PI

# Other Imports
import json
import numpy as np


def load_sensor_suite_from_json(filename: str, manager: 'WASensorManager'):
    """Load a sensor suite from json

    Args:
        filename (str): The json specification file that describes the sensor suite
        manager (WASensorManager): The sensor manager to store all created objects in
    """
    j = load_json(get_wa_data_file(filename))

    # Validate the json file
    check_field(j, 'Type', value='Sensor')
    check_field(j, 'Template', value='Sensor Suite')
    check_field(j, 'Sensors', field_type=list)

    # Load the sensors
    for sensor in j['Sensors']:
        new_sensor = load_sensor_from_json(sensor, manager.vehicle)
        manager.add_sensor(new_sensor)


def load_sensor_from_json(filename: str, vehicle: WAVehicle):
    """Load a sensor from json

    Args:
        filename (str): The json specification file that describes the sensor
        vehicle (WAVehicle): The vehicle each sensor will be attached to
    """
    j = load_json(get_wa_data_file(filename))

    # Validate the json file
    check_field(j, 'Type', value='Sensor')
    check_field(j, 'Template', allowed_values=['IMU', 'GPS'])

    # Check the template and create a sensor based off what it is
    if j['Template'] == 'IMU':
        sensor = WAIMUSensor(vehicle, filename)
    elif j['Template'] == 'GPS':
        sensor = WAGPSSensor(vehicle, filename)
    else:
        raise TypeError(f"{j['Template']} is not an implemented sensor type")

    return sensor


class WASensorManager:
    """Base class that manages sensors.

    Args:
        system (WASystem): The system for the simulation
        filename (str): A json file to load a scene from. Defaults to None (does nothing).

    Attributes:
        system (WASystem): The system for the simulation
        vehicle (WAVehicle): The vehicle each sensor will be attached to
        sensors (list): List of the attached sensors
    """

    # Global filenames for sensor suites
    EGP_SENSOR_SUITE_FILE = "sensors/suites/ev_grand_prix.json"

    def __init__(self, system: WASystem, vehicle: WAVehicle, filename: str = None):
        self.system = system
        self.vehicle = vehicle

        self.sensors = []

        if filename is not None:
            load_sensor_suite_from_json(filename, self)

    def add_sensor(self, sensor: "WASensor"):
        """Add a sensor to the sensor manager"""
        self.sensors.append(sensor)

    def synchronize(self, time):
        """Synchronize the sensor at the specified time

        Args:
            time (float): the time at which the sensors are synchronized to
        """
        for sensor in self.sensors:
            sensor.synchronize(time)

    def advance(self, step):
        """Advance the state of the sensor by the specified time step

        Args:
            step (float): the step to update the sensor by
        """
        for sensor in self.sensors:
            sensor.advance(step)


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
        check_field(p, 'Noise Type', value='Normal Drift')
        check_field(p, 'Update Rate', field_type=float)
        check_field(p, 'Mean', field_type=list)
        check_field(p, 'Standard Deviation', field_type=list)
        check_field(p, 'Bias Drift', field_type=float)
        check_field(p, 'Tau Drift', field_type=float)

        self._load_properties(p)

    def _load_properties(self, p: dict):
        """Private function that loads propeties and sets them to class variables

        Args:
            p (dict): Propeties dictionary
        """
        self.update_rate = p['Update Rate']
        self.mean = WAVector(p['Mean'])
        self.sigma = WAVector(p['Standard Deviation'])
        self.bias_drift = p['Bias Drift']
        self.tau_drift = p['Tau Drift']

        self.bias = WAVector()

    def add_noise(self, data: list):
        """Add noise to the data

        Args:
            data (list): The data to add noise to
        """

        def rand(element):
            return np.random.normal(getattr(self.mean, element, 0), getattr(self.sigma, element, 0))

        eta_a = WAVector([rand('x'), rand('y'), rand('z')])

        eta_b = WAVector()
        if self.tau_drift > 0 and self.bias_drift > 0:
            def rand(): return np.random.normal(0.0, self.drift_bias * np.sqrt(1.0 / (self.update_rate * self.tau_drift)))  # noqa
            eta_b = WAVector([rand(), rand(), rand()])

        self.bias += eta_b
        data += eta_a + self.bias


class WANormalNoiseModel(WANoiseModel):
    """Derived noise model. Gaussian drifting noise with noncorrelated equal distributions

    Very similar to ChNormalModel (https://github.com/projectchrono/chrono/blob/feature/sensor/src/chrono_sensor/ChNoiseModel.h)
    Made because ChSensor currently _requires_ OptiX (NVIDIA proprietary software)

    Args:
        p (dict): Model properties/parameters taken from a json specification file
    """

    def __init__(self, p: dict):
        # Validate properties
        check_field(p, 'Noise Type', value='Normal')
        check_field(p, 'Mean', field_type=list)
        check_field(p, 'Standard Deviation', field_type=list)

        self._load_properties(p)

    def _load_properties(self, p: dict):
        """Private function that loads propeties and sets them to class variables

        Args:
            p (dict): Propeties dictionary
        """
        self.mean = WAVector(p['Mean'])
        self.sigma = WAVector(p['Standard Deviation'])

    def add_noise(self, data: list):
        """Add noise to the data

        Args:
            data (list): The data to add noise to
        """

        def rand(element):
            return np.random.normal(getattr(self.mean, element, 0), getattr(self.sigma, element, 0))

        data += WAVector([rand('x'), rand('y'), rand('z')])


class WASensor(ABC):
    """Base class for a sensor"""

    def __init__(self):
        pass

    @abstractmethod
    def synchronize(self, time):
        """Synchronize the sensor at the specified time

        Args:
            time (float): the time at which the sensors are synchronized to
        """
        pass

    @abstractmethod
    def advance(self, step):
        """Advance the state of the sensor by the specified time step

        Args:
            step (float): the step to update the sensor by
        """
        pass

    @abstractmethod
    def get_data(self):
        """Get the sensor data"""
        pass


class WAIMUSensor(WASensor):
    """Derived sensor class that implements an IMU model

    Args:
        vehicle (WAVehicle): the vehicle that the state data will be extracted from
        filename (str): a json specification file that describes an IMU sensor model
    """

    # Global filenames for imu sensors
    SBG_IMU_SENSOR_FILE = "sensors/models/SBG_IMU.json"

    def __init__(self, vehicle: WAVehicle, filename: str):
        self.vehicle = vehicle

        j = load_json(get_wa_data_file(filename))

        # Validate the json file
        check_field(j, 'Type', value='Sensor')
        check_field(j, 'Template', value='IMU')
        check_field(j, 'Properties', field_type=dict)

        p = j['Properties']
        check_field(p, 'Update Rate', field_type=int)
        check_field(p, 'Noise Model', field_type=dict, optional=True)

        if 'Noise Model' in p:
            check_field(p['Noise Model'], 'Noise Type',
                        allowed_values=["Normal", "Normal Drift"])

        self._load_properties(p)

        self.acc = WAVector()
        self.omega = WAVector()
        self.orientation = WAVector()

    def _load_properties(self, p: dict):
        """Private function that loads properties and sets them to class variables

        Args:
            p (dict): Properties dictionary
        """
        self.update_rate = p['Update Rate']

        self.noise_model = WANoNoiseModel()
        if 'Noise Model' in p:
            n = p['Noise Model']

            if n['Noise Type'] == 'Normal Drift':
                self.noise_model = WANormalDriftNoiseModel(n)
            elif n['Noise Type'] == 'Normal':
                self.noise_model = WANormalNoiseModel(n)
            else:
                raise TypeError(
                    f"{p['Noise Type']} is not an implemented model type")

    def synchronize(self, time):
        """Synchronize the sensor at the specified time

        Args:
            time (float): the time at which the sensors are synchronized to
        """
        self.noise_model.add_noise(self.acc)  # Acceleration (accelerometer)
        self.noise_model.add_noise(self.omega)  # Angular velocity (gyroscope)
        # self.noise_model.add_noise(self.orientation)  # Orientation ("Magnometer") # noqa

    def advance(self, step):
        """Advance the state of the sensor by the specified time step

        Args:
            step (float): the step to update the sensor by
        """
        self.acc = self.vehicle._get_acceleration()
        self.omega = self.vehicle._get_angular_velocity()
        self.orientation = self.vehicle._get_orientation()

    def get_data(self):
        """Get the sensor data

        Returns:
            (WAVector, WAVector, WAQuaternion): Tuple in the form of (acceleration, angular_velocity, orientation)
        """
        return self.acc, self.omega, self.orientation


class WAGPSSensor(WASensor):
    """Derived sensor class that implements an GPS model

    Args:
        vehicle (WAVehicle): the vehicle that the state data will be extracted from
        filename (str): a json specification file that describes an IMU sensor model
    """

    # Global filenames for gps sensors
    SBG_GPS_SENSOR_FILE = "sensors/models/SBG_GPS.json"

    def __init__(self, vehicle: WAVehicle, filename: str):
        self.vehicle = vehicle

        j = load_json(get_wa_data_file(filename))

        # Validate the json file
        check_field(j, 'Type', value='Sensor')
        check_field(j, 'Template', value='GPS')
        check_field(j, 'Properties', field_type=dict)

        p = j['Properties']
        check_field(p, 'Update Rate', field_type=int)
        check_field(p, 'GPS Reference', field_type=list)
        check_field(p, 'Noise Model', field_type=dict, optional=True)

        if 'Noise Model' in p:
            check_field(p['Noise Model'], 'Noise Type',
                        allowed_values=["Normal", "Normal Drift"])

        self._load_properties(p)

    def _load_properties(self, p: dict):
        """Private function that loads properties and sets them to class variables

        Args:
            p (dict): Properties dictionary
        """
        self.update_rate = p['Update Rate']
        self.reference = WAVector(p['GPS Reference'])

        self.noise_model = WANoNoiseModel()
        if 'Noise Model' in p:
            n = p['Noise Model']

            if n['Noise Type'] == 'Normal Drift':
                self.noise_model = WANormalDriftNoiseModel(n)
            elif n['Noise Type'] == 'Normal':
                self.noise_model = WANormalNoiseModel(n)
            else:
                raise TypeError(
                    f"{p['Noise Type']} is not an implemented model type")

        self.pos = WAVector()

    def synchronize(self, time):
        """Synchronize the sensor at the specified time

        Args:
            time (float): the time at which the sensors are synchronized to
        """
        self.noise_model.add_noise(self.pos)

    def advance(self, step):
        """Advance the state of the sensor by the specified time step

        Args:
            step (float): the step to update the sensor by
        """
        self.pos = self.vehicle._get_position()
        self.coord = WAGPSSensor.cartesian_to_gps(self.pos, self.reference)

    def get_data(self):
        """Get the sensor data

        Returns:
            WAVector: The coordinate location of the vehicle in the form of [longitude, latitude, altitude]
        """
        return self.coord

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
