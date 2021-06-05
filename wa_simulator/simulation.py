"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

from abc import ABC, abstractmethod  # Abstract Base Class
import multiprocessing.connection as mp
from pyrr import Vector3, Quaternion

# WA Simulator
from wa_simulator.base import WABase
from wa_simulator.vehicle import WAVehicle
from wa_simulator.sensor import WASensorManager, WAIMUSensor, WAGPSSensor
from wa_simulator.controller import WAExternalController


class WASimulationManager(WABase):
    """A manager for a simulation. Advances and synchronizes simulation modules.

    The simulation manager is used primarily for cleaning up demo and runner files.
    Typically, users do not want to have all update methods(synchronize / advance) in their actual demo file, as that would convalute the
    demo and make things more complicated. This class aims to simplify these scenarios
    buy wrapping update related method calls not necessarily relevant to the user.

    This class constructor (the :code:`__init__` method) has two actual arguments: :code:`*args` and :code:`**kwargs`.
    These two arguments have special attributes not relevant in other languages, so for more
    information on those, please see `this reference <https://www.digitalocean.com/community/tutorials/how-to-use-args-and-kwargs-in-python-3>`_.

    Although not techincally an error, this class should not be inherited from.

    Args:
        system (WASystem): the system that has meta properties such as time and render step size
        *args: Positional arguments made up of WABase classes. An exception will be thrown if the components are not WABase level classes
        record (boolean): Log simulation data as a csv?
        output_filename (str): Only used if record is true. If record is true and this is empty, an exception will be raised.

    Raises:
        ValueError: If any one of the positional arguments does not derive from WABase (`see classes that do <google.com>`_).
        ValueError: If record is true but output_filename is empty.

    .. todo::
        - Add link to all WABase classes

    Examples:

    .. highlight:: python
    .. code-block:: python

        import wa_simulator as wa

        ... # Initialization of subcomponents

        # Ex 1.
        manager = wa.WASimulationManager(
            vehicle, visualization, system, controller, environment)

        # Ex 2.
        manager = wa.WASimulationManager(sensor_manager, system, environment)

        # Ex 3.
        # WARNING: Recording is not currently supported
        manager = wa.WASimulationManager(vehicle, visualization, system, controller,
                                     environment, sensor_manager, record=True, output_filename="example.csv")
    """

    def __init__(self, system: 'WASystem', *args, record: bool = False, output_filename: str = "", enable_external: bool = False, external_message_frequency: float = 20.0):
        self._system = system
        self._enable_external = enable_external
        self._external_send_step = 1.0/external_message_frequency
        self._time_since_sent_external = 0.0

        self._components = []
        self._external_controllers = {}

        for i, comp in enumerate(args):
            if comp is None:
                continue

            # Check to make sure each element derives from WABase
            if not isinstance(comp, WABase):
                raise TypeError(
                    f'Argument in position {i} is of type {type(comp)}, not {type(WABase)}.')
            elif isinstance(comp, WASimulationManager):
                raise TypeError(
                    f'Argument in position {i} is of type {type(WASimulationManager)}. This is not allowed')

            self._components.append(comp)

            # Save the external controllers for quicker access
            if isinstance(comp, WAExternalController):
                self._external_controllers[comp.external_id] = comp

        self.set_record(record, output_filename)

        # Setup the external connection
        if self._enable_external:
            print("Waiting for external connection to localhost:5555...")
            self._external_address = ('localhost', 5555)
            self._external_listener = mp.Listener(self._external_address)
            self._external_connection = self._external_listener.accept()
            print("Accepted connection")

            # Only once, we need to tell the rosnode what topics to subscribe to for the controllers
            msg = {
                "type": "controller_ids",
                "data": {
                    "ids": [controller_id for controller_id in self._external_controllers.keys()]
                }
            }
            self._external_connection.send(msg)

    def synchronize(self, time: float):
        for comp in self._components:
            comp.synchronize(time)
            self._receive_external()

    def advance(self, step: float):
        self._system.advance()

        for comp in self._components:
            comp.advance(step)
            self._send_external(comp, step)

    def is_ok(self) -> bool:
        for comp in self._components:
            if not comp.is_ok():
                return False
        return self._system.is_ok()

    def run(self):
        """Helper method that runs a simulation loop. 

        It's recommended to just use :meth:`~synchronize` and :meth:`~advance` to remain explicit in intent,
        but this method can also be used to update states of components. Basically, this method will just
        call the :meth:`~synchronize` and :meth:`~advance` functions in a :code:`while` loop until any components
        fail.
        """
        step_size = self._system.step_size
        while self.is_ok():
            time = self._system.time

            self.synchronize(time)
            self.advance(step_size)

    def record(self):
        """Perform a record step for each component active in the simulation.

        .. warning::
            Currently not implemented
        """
        pass

    def set_record(self, record: bool = True, output_filename: str = ""):
        """Specify whether the simulation should be recorded.

        Args:
            record (bool): record the simulation?
            output_filename (str): the csv filename to save data to. If record is true and this is empty, an exception will be raised
        """
        self._record = record
        self._output_filename = output_filename

        if record and len(output_filename) == 0:
            raise AttributeError(
                "record has been set to 'True', but output_filename is empty.")

    def _send_external(self, comp, time_step):
        """
        I feel like we should use a more general way to pass these messages. Like protobuf, as then it is
        portable to whatever external process wants to talk to it.

        ToDo: Have a settable frequency for each sensor (at least for external publishing)

        ToDo: Camera and lidar (need to compile chrono from source)
        """
        if not self._enable_external:
            return

        if(self._time_since_sent_external >= self._external_send_step):
            self._time_since_sent_external = 0.0
        else:
            self._time_since_sent_external += time_step
            return

        if isinstance(comp, WAVehicle):
            msg = {
                "type": "vehicle_state",
                "data": {
                    "id": comp.external_id,
                    "position": Vector3(comp.get_pos()),
                    "rotation": Quaternion(comp.get_rot()),
                    "linear_velocity": Vector3(comp.get_pos_dt()),
                    "angular_velocity": Vector3(comp.get_rot_dt()),
                    "linear_acceleration": Vector3(comp.get_pos_dtdt()),
                    "angular_acceleration": Vector3(comp.get_rot_dtdt())
                }
            }
            self._external_connection.send(msg)
        elif isinstance(comp, WASensorManager):
            for sensor in comp._sensors:
                if isinstance(sensor, WAIMUSensor):
                    linear_acceleration, angular_velocity, orientation = sensor.get_data()
                    msg = {
                        "type": "imu_sensor",
                        "data": {
                            "id": sensor.external_id,
                            "linear_acceleration": Vector3(linear_acceleration),
                            "angular_velocity": Vector3(angular_velocity),
                            "orientation": Quaternion(orientation)
                        }
                    }
                    self._external_connection.send(msg)
                elif isinstance(sensor, WAGPSSensor):
                    msg = {
                        "type": "gps_sensor",
                        "data": {
                            "id": sensor.external_id,
                            "coordinates": Vector3(sensor.get_data())
                        }
                    }
                    self._external_connection.send(msg)


    def _receive_external(self):

        if not self._enable_external:
            return

        # Check if new data is available
        while self._external_connection.poll():
            msg = self._external_connection.recv()

            if not "type" in msg.keys():
                print(f"No message type specified in: {msg}")
                return

            if msg["type"] == "vehicle_control":
                # msg = {
                #     "type": "vehicle_control",
                #     "data": {
                #         "steering": 0.0,
                #         "throttle": 0.01,
                #         "braking": 0.0
                #     }
                # }
                vehicle_id = msg["data"]["id"]
                steering = msg["data"]["steering"]
                throttle = msg["data"]["throttle"]
                braking = msg["data"]["braking"]
                if not vehicle_id in self._external_controllers.keys():
                    return
                controller = self._external_controllers[vehicle_id]
                controller.steering = steering
                controller.throttle = throttle
                controller.braking = braking
