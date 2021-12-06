"""
Wisconsin Autonomous - https://wa.wisc.edu

Copyright (c) 2021 wa.wisc.edu
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# WA Simulator
from wa_simulator.base import WABase
from wa_simulator.utils import _check_type

# External Imports
import multiprocessing.connection as mp
from typing import Callable, Dict, Tuple, Any, List, Union

import sys


class WABridge(WABase):
    """Base class for a bridge interface between the simulator and an external entity

    There are many applications where it's desired that :code:`wa_simulator` communicates with external entities.
    For example, `Robot Operating System or ROS <https://www.ros.org/>`_ is a popular tool for writing
    robotic control code. Simulation is a very valuable tool for testing, so being able to communicate
    with these external control stacks is an important feature.

    For each external entity that wants to be connected to, a new bridge object must be created. The :code:`multiprocessing.connection` library
    will be used and it's `Listener <https://docs.python.org/3/library/multiprocessing.html#multiprocessing.connection.Listener>`_ class.
    The messages will be sent as dictionaries of data and messages to be sent at each timestep will be accumulated to be sent as one large message.

    Message types are dynamic in types, form and structure; however, there are a few rules that must be abided by. First, sender names must be unique. The
    name will be used as the message identifier in the dictionary. Second, the structure of the message types will be infered, if possible. Otherwise, they must be
    explicitely provided in the calling method when adding the sender.

    Args:
        system (WASystem): The system used to manage the simulation
        hostname (str): The hostname of the client entity
        port (int): The port to attach to
        use_ack (bool): Specify whether to use an acknowledgement when sending a message to ensure the client got the message. Defaults to True.
        is_synchronous(bool): Specify whether the sender and receivers are in synchronous mode. If yes, on each step, a message will be sent and received. If not, will not wait for a message to be received.
        ignore_unknown_messages (bool): If a message is received with an unknown name (not registered with :meth:`~add_receiver`), ignore it. Defaults to True. If False, will raise an error.
    """

    def __init__(self, system: 'WASystem', hostname: str = 'localhost', port: int = 5555, server: bool = True, use_ack: bool = True, is_synchronous : bool = True, ignore_unknown_messages: bool = True):
        self._system = system

        self._hostname = hostname
        self._port = port
        self._address = (self._hostname, self._port)
        self._server = server

        self._use_ack = use_ack
        self._is_synchronous = is_synchronous
        self._timeout = 2 # Default timeout is 2 seconds

        self._ignore_unknown_messages = ignore_unknown_messages

        self._senders: Dict[str, Tuple[WABase, Callable[[WABase], dict]]] = {}
        self._senders["system"] = (
            self._system, self._message_generators['WASystem'])

        self._receivers: Dict[str, Tuple[Any, Callable[[Any, dict], dict]]] = {}
        self._global_receivers: List[Tuple[Any, Callable[[str, Any], None]]] = []

        self._connection = None

    def connect(self):
        """Method that connects with the external entity.

        Typically called by :class:`~WASimulationManager`, but okay to call outside. Will only connect to one client at
        the hostname and port provided to the constructor.

        If this bridge is a server, a ``multiprocessing.Connection.Listener`` object is used. Otherwise, a ``multiprocessing.Connection.Client`` object is used.
        See the `Listener <https://docs.python.org/3/library/multiprocessing.html#multiprocessing.connection.Listener>`_ 
        or `Client <https://docs.python.org/3/library/multiprocessing.html#multiprocessing.connection.Client>`_ docs to see possible errors that may be raised.
        """
        if self._server:
            self._listener = mp.Listener(self._address)
            self._connection = self._listener.accept()
        else:
            self._connection = mp.Client(self._address)

    def add_sender(self, name: str, component: WABase, message_generator: Callable[[WABase], dict] = None):
        """Adds a sender component that has outgoing messages

        To actually send data from the simulation to the external client, this method (or it's derivatives) must be called
        to explicitly tell the bridge what information to send. 

        The format of the outgoing message is inferred, unless ``message_generator`` is not ``None``. If the message structure cannot
        be inferred and ``message_generator`` is ``None``, a ``RuntimeError`` will be raised.

        Args:
            name (str): The unique message name/identifier (think ROS topic)
            component (WABase): The :class:`~WABase` component the message data will be generated from
            message_generator (Callable[[WABase], dict]): A custom method that generates a dict message to be sent from the specified component

        Raises:
            ValueError: if ``name`` is not unique (there is already a message identifier with that name)
            RuntimeError: If the message structure cannot be inferred and a message generator method is not provided
        """

        if name in self._senders:
            raise ValueError(
                f"Sender must have a unique name. {name} already exists.")

        _class_name = self._get_base_name(component)
        if _class_name not in self._message_generators and message_generator is None:
            raise RuntimeError(
                f"The outgoing message structure cannot be inferred for '{_class_name}' and a message generator method was not provided.")

        if message_generator is None:
            message_generator = self._message_generators[_class_name]

        self._senders[name] = (component, message_generator)

    def add_receiver(self, name: str = "", element: Any = None, message_parser: Callable[[Any], dict] = None):
        """Adds a receiver element that has incoming messages

        A receiver either has a name and element, a name, element and message_perser, or just a message_parser. If a name
        and element are provided, the message_parser is attempted to be inferred. If it can't be inferred, a error will be raised.
        If it can't be inferred, you should provied a message_parser. The name will be used to determine what message_parser to call when 
        a message is received. If neither a name or element are provided, a message_parser must be provided. In this case, a
        all received messages that do not have a callback will call this message_parser. Think of this as a 'global message listener'.

        The ``name`` need not be unique from any senders in the class, only from other receivers.

        "element" is used instead of "component" because the element doesn't necessarily need to be a WABase derived class.

        On each synchronization step, the receiver message parse method will be called. To have the listener be polled for messages,
        a single receiver must be added. Further, for the receiver parser to be called, the name attached to the message and the receiver
        added here must match. If there is no match, either the message will be ignored (unless ``ignore_unknown_messages`` is set to fault in
        the constructor) or if there is a global message listener, it's callback will be called.

        The format of the incoming message is inferred, unless ``message_parser`` is not ``None``. If the message structure cannot
        be inferred and ``message_parser`` is ``None``, a ``RuntimeError`` will be raised.

        Args:
            name (str): The unique message name/identifier (think ROS topic)
            element (Any): The element the message data will be used to populate or change. Should be an object so it's passed by reference.
            message_parser (Callable[[Any], Any]): A custom method that parses the received messag

        Raises:
            ValueError: if ``name`` is not unique (there is already a message identifier with that name)
            RuntimeError: If the message structure cannot be inferred and a message parser method is not provided
        """

        if name != "" and element is not None:
            if name in self._receivers:
                raise ValueError(
                    f"Receiver must have a unique name. {name} already exists.")

            _class_name = element.__class__.__name__
            if _class_name not in self._message_parsers and message_parser is None:
                raise RuntimeError(
                    f"The incoming message structure cannot be inferred for '{_class_name}' and a message parser method was not provided.")

            if message_parser is None:
                message_parser = self._message_parsers[_class_name]

            self._receivers[name] = (element, message_parser)
        elif message_parser is not None:
            self._global_receivers.append(message_parser)
        else:
            raise ValueError(f"'name' and/or 'element' are unset and a message_parser was not provided.")

    def synchronize(self, time: float):
        """Synchronizes with the external entity

        Will accumulate the messages to be sent and then send them. And then will receive any messages
        from receivers.

        Raises:
            RuntimeError: If an acknowledgement is not received from the client after data is sent or it is corrupt.
        """
        if self._server:
            self._receive()
        else:
            self._send()

    def advance(self, step: float):
        """Advance the state of the bridge

        Will receive any messages from the client, if there are registered receivers.

        Raises:
            RuntimeError: Received an unknown message (only if ignore_unknown_messages is False)
        """
        if self._server:
            self._send()
        else:
            self._receive()

    def _send(self):
        if self._connection is None:
            raise RuntimeError("Bridge was not been connected to client. Please call connect!")

        # Send messages
        message = {}
        for name, (component, message_generator) in self._senders.items():
            generated_message = message_generator(component)
            if generated_message:
                message.update({name: generated_message})
        self._connection.send(message)

        if self._use_ack:
            # Receive an acknowledgement that we got the message
            if not self._connection.poll(self._timeout):
                raise RuntimeError(
                    "Failed to receive acknowledgement from client.")
            ack = self._connection.recv()
            if ack != 1:
                raise RuntimeError("Acknowledgement is corrupted.")


    def _receive(self):
        # Receive messages
        if len(self._receivers) or len(self._global_receivers):
            # If in synchronous mode, throw an error if we don't receive a message
            if self._is_synchronous and not self._connection.poll(self._timeout):
                raise RuntimeError("Failed to receive acknowledgement from client.")

            # If not in synchronous mode, make sure we have received a message
            if self._is_synchronous or (not self._is_synchronous and self._connection.poll()):
                data = self._connection.recv()
                for name, message in data.items():
                    if name in self._receivers:
                        element, message_parser = self._receivers[name]
                        message_parser(element, message)
                    elif len(self._global_receivers):
                        for message_parser in self._global_receivers:
                            message_parser(name, message)
                    elif not self._ignore_unknown_messages:
                        raise RuntimeError(
                            "Received unknown message. Choosing not to ignore.")

                if self._use_ack:
                    self._connection.send(1)

    def is_ok(self) -> bool:
        return True

    def set_timeout(self, timeout: bool):
        """Set the timeout for the acknowledgement

        If acknowledgements are utilized, the timeout value is used to determine how long to wait before throwing an error that an ack was never received. This 
        method provides the ability to set this value.

        Args:
            timeout (bool): The new timeout value
        """
        self._timeout = timeout

    def _get_base_name(self, component):
        """
        Attempts to grab the base class immediately following WABase.
        Like we want WAVehicle rather than WALinearKinematicVehicle
        NOTE: did not test throughly
        """
        mro = component.__class__.__mro__  # method resolution
        for c in mro[-1::-1]:
            name = c.__name__
            if name in self._message_generators:
                return name
        return component.__class__.__name__

    # -----------------------------
    # Inferrable message generators
    # -----------------------------
    _message_generators: Dict[str, Callable[[WABase], dict]] = {}

    def _message_generator_WASystem(component: 'WASystem') -> dict:
        return {
            "type": "WASystem",
            "data": {
                    "time": component.time,
                    "step_number": component.step_number
            }
        }
    _message_generators['WASystem'] = _message_generator_WASystem

    def _message_generator_WAVehicle(component: 'WAVehicle') -> dict:
        return {
            "type": "WAVehicle",
            "data": {
                    "position": component.get_pos(),
                    "rotation": component.get_rot(),
                    "linear_velocity": component.get_pos_dt(),
                    "angular_velocity": component.get_rot_dt(),
                    "linear_acceleration": component.get_pos_dtdt(),
                    "angular_acceleration": component.get_rot_dtdt(),
            }
        }
    _message_generators['WAVehicle'] = _message_generator_WAVehicle

    def _message_generator_WAIMUSensor(component: 'WAIMUSensor') -> dict:
        data = component.get_data()
        if data is None:
            # The sensor may not have any data available, so it may return None
            # If that's the case, return an empty dict
            return {}

        return {
            "type": "WAIMUSensor",
            "data": {
                "linear_acceleration": data[0],
                "angular_velocity": data[1],
                "orientation": data[2],
            }
        }
    _message_generators['WAIMUSensor'] = _message_generator_WAIMUSensor

    def _message_generator_WAGPSSensor(component: 'WAGPSSensor') -> dict:
        data = component.get_data()
        if data is None:
            # The sensor may not have any data available, so it may return None
            # If that's the case, return an empty dict
            return {}

        return {
            "type": "WAGPSSensor",
            "data": {
                "latitude": data[0],
                "longitude": data[1],
                "altitude": data[2]
            }
        }
    _message_generators['WAGPSSensor'] = _message_generator_WAGPSSensor

    def _message_generator_WAVehicleInputs(component: 'WAVehicleInputs') -> dict:
        return {
            "type": "WAVehicleInputs",
            "data": {
                "steering": component.steering,
                "throttle": component.throttle,
                "braking": component.braking,
            }
        }
    _message_generators['WAVehicleInputs'] = _message_generator_WAVehicleInputs

    # --------------------------
    # Inferrable message parsers
    # --------------------------
    _message_parsers: Dict[str, Callable[[Any, dict], Any]] = {}

    def _message_parser_WAVehicleInputs(element: 'WAVehicleInputs', message: dict) -> Any:
        element.steering = message["data"]["steering"]
        element.throttle = message["data"]["throttle"]
        element.braking = message["data"]["braking"]
        return element
    _message_parsers['WAVehicleInputs'] = _message_parser_WAVehicleInputs

    def _message_parser_dict(element: 'dict', message: dict) -> Any:
        element.update(message)
        return element
    _message_parsers['dict'] = _message_parser_dict
