"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# WA Simulator
from wa_simulator.utils import check_type, load_json, check_field, get_wa_data_file
from wa_simulator.sensor import WASensorManager, WASensor, load_sensor_from_json
from wa_simulator.chrono.vehicle import WAChronoVehicle
from wa_simulator.chrono.utils import ChVector_from_list, ChFrame_from_json
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
        msg = f"{function_name}: Requires Chrono::Sensor and was not found. Chrono::Sensor requires build Chrono from source. Consult Aaron Young (aryoung5@wisc.edu) if you have questions."
        raise RuntimeError(msg)


def load_chrono_sensor_scene_from_json(filename: str, manager: "WAChronoSensorManager"):
    """Load a chrono sensor scene from a json specification file. A scene may consist of "World" attributes (i.e. lights) or sensors

    Args:
        filename (str): The json specification file describing the scene
        manager (WASensorManager): The sensor manager to edit the scene of
    """
    if missing_chrono_sensor:
        sens_import_error('load_chrono_sensor_scene_from_json')

    j = load_json(filename)

    # Validate the json file
    check_field(j, 'Type', value='Sensor')
    check_field(j, 'Template', value='Chrono Sensor Scene')
    check_field(j, 'World', field_type=dict, optional=True)
    check_field(j, 'Sensors', field_type=list, optional=True)
    check_field(j, 'Objects', field_type=list, optional=True)

    if 'World' in j:
        w = j['World']

        check_field(w, 'Point Lights', field_type=list)

        # Create the point lights
        # NOTE: Might be optional in the future
        for p in w['Point Lights']:
            check_field(p, 'Position', field_type=list)
            check_field(p, 'Color', field_type=list)
            check_field(p, 'Maximum Range', field_type=float)

            pos = ChVector_from_list(p['Position'], chrono.ChVectorF)
            color = ChVector_from_list(p['Color'], chrono.ChVectorF)
            max_range = p['Maximum Range']

            manager.manager.scene.AddPointLight(pos, color, max_range)

    if 'Sensors' in j:
        s = j['Sensors']

        for sensor in s:
            new_sensor = load_chrono_sensor_from_json(
                sensor, manager.vehicle)
            manager.add_sensor(new_sensor)

    if 'Objects' in j:
        objects = j['Objects']

        for o in objects:
            check_field(o, 'Size', field_type=list)
            check_field(o, 'Position', field_type=list)
            check_field(o, 'Color', field_type=list, optional=True)
            check_field(o, 'Texture', field_type=str, optional=True)

            size = ChVector_from_list(o['Size'])
            pos = ChVector_from_list(o['Position'])

            box = chrono.ChBodyEasyBox(size.x, size.y, size.z, 1000, True, False)  # noqa
            box.SetPos(pos)
            if 'Color' in o:
                c = ChVector_from_list(o['Color'])
                box.AddAsset(chrono.ChColorAsset(chrono.ChColor(c.x, c.y, c.z)))  # noqa
            if 'Texture' in o:
                texture = chrono.ChVisualMaterial()
                texture.SetKdTexture(get_wa_data_file(o['Texture']))
                chrono.CastToChVisualization(box.GetAssets()[0]).material_list.append(texture)  # noqa
            box.SetBodyFixed(True)

            manager.add_body(box)


def load_chrono_sensor_from_json(filename: str, vehicle: WAChronoVehicle):
    """Load a chrono sensor from json

    If the passed json file isn't a chrono type, it will call the correct method.

    Args:
        filename (str): The json specification file that describes the sensor
        vehicle (WAChronoVehicle): The vehicle each sensor will be attached to
    """
    if missing_chrono_sensor:
        sens_import_error('load_chrono_sensor_from_json')

    # Check if the file can be found in the chrono portion of the data folder
    try:
        j = load_json(chrono.GetChronoDataFile(filename))
    except FileNotFoundError:
        # File is not chrono specific, try that now
        j = load_json(get_wa_data_file(filename))
        return load_sensor_from_json(filename, vehicle)

    return WAChronoSensor(vehicle, filename)


class WAChronoSensorManager(WASensorManager):
    """Derived SensorManager class that essentially wraps a ChSensorManager. Used to maintain sensors.

    Args:
        system (WAChronoSystem): The system for the simulation
        vehicle (WAVehicle): The vehicle each sensor is attached to
        filename (str): A json file to load a scene from. Defaults to None (does nothing).

    Attributes:
        manager (ChSensorManager): The chrono sensor manager that actually performs the updates of the chrono objects
        system (WAChronoSystem): The system for the simulation
        vehicle (WAChronoVehicle): The vehicle each sensor is attached to
        filename (str): A json file to load a scene from. Defaults to None (does nothing).
    """

    # Global filenames for environment models
    EGP_SENSOR_SCENE_FILE = chrono.GetChronoDataFile("sensors/scenes/ev_grand_prix.json")  # noqa

    def __init__(self, system: WAChronoSystem, vehicle: WAChronoVehicle, filename: str = None):
        if missing_chrono_sensor:
            sens_import_error('WAChronoSensorManager.__init__')

        check_type(system, WAChronoSystem, 'system', 'WAChronoSensorManager.__init__')  # noqa
        check_type(vehicle, WAChronoVehicle, 'vehicle', 'WAChronoSensorManager.__init__')  # noqa

        super().__init__(system, vehicle)

        self.system = system
        self.vehicle = vehicle

        self.bodies = []

        self.manager = sens.ChSensorManager(self.system.system)

        if filename is not None:
            load_chrono_sensor_scene_from_json(filename, self)

    def add_sensor(self, sensor: "WAChronoSensor"):
        """Add a sensor to the sensor manager"""
        if isinstance(sensor, WAChronoSensor):
            self.manager.AddSensor(sensor.sensor)
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
        self.manager.Update()

        super().advance(step)

    def add_body(self, body):
        """Adds a ChBody to the ChSystem. Saves them to be used later"""
        self.system.system.Add(body)
        self.bodies.append(body)


class WAChronoSensor(WASensor):
    """Derived Sensor class that is still abstract that essentially wraps a ChSensor"""

    # Global filenames for various sensors
    MONO_CAM_SENSOR_FILE = "sensors/models/generic_monocamera.json"
    LDMRS_LIDAR_SENSOR_FILE = "sensors/models/ldmrs.json"

    def __init__(self, vehicle: WAChronoVehicle, filename: str):
        if missing_chrono_sensor:
            sens_import_error('WAChronoSensor.__init__')

        filename = chrono.GetChronoDataFile(filename)
        j = load_json(filename)

        # Validate the json file
        check_field(j, 'Type', value='Sensor')
        check_field(j, 'Template', allowed_values=['Camera', 'Lidar', 'IMU', 'GPS'])  # noqa
        check_field(j, 'Offset Pose', field_type=dict)

        offset_pose = ChFrame_from_json(j['Offset Pose'])

        # Create the chrono sensor through the Sensor chrono class
        self.sensor = sens.Sensor.CreateFromJSON(filename, vehicle.vehicle.GetChassisBody(), offset_pose)  # noqa

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
        name = self.sensor.GetName().lower()
        if 'camera' in name:
            buff = self.sensor.GetMostRecentRGBA8Buffer()
            return buff.GetRGBA8Data()
        if 'lidar' in name:
            buff = self.sensor.GetMostRecentXYZIBuffer()
            return buff.GetXYZIData()
        else:
            raise TypeError(
                f"WAChronoSensorManager.get_data: can't determine sensor type from name: '{name}'.")
