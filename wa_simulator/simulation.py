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
from wa_simulator.bridge import WABridge


class WASimulationManager(WABase):
    """A manager for a simulation. Advances and synchronizes simulation modules.

    The simulation manager is used primarily for cleaning up demo and runner files.
    Typically, users do not want to have all update methods(synchronize / advance) in their actual demo file, as that would convalute the
    demo and make things more complicated. This class aims to simplify these scenarios
    buy wrapping update related method calls not necessarily relevant to the user.

    This class constructor (the :code:`__init__` method) has two actual arguments: :code:`*args` and :code:`**kwargs`.
    These two arguments have special attributes not relevant in other languages, so for more
    information on those, please see `this reference <https://www.digitalocean.com/community/tutorials/how-to-use-args-and-kwargs-in-python-3>`_.

    If any of the components passed in are of type :class:`~WABridge`, the simulation manager will first wait until the bridge establishes a 
    connection with it's client. The simulation will then be allowed to progress once this has been completed.

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

    def __init__(self, system: 'WASystem', *args, record: bool = False, output_filename: str = ""):
        self._system = system

        self._components = []
        self._bridges = []
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

            # Save the bridges for connection purposes
            if isinstance(comp, WABridge):
                self._bridges.append(comp)

            self._components.append(comp)

        # Make sure all the bridges connect first
        for bridge in self._bridges:
            bridge.connect()

        self.set_record(record, output_filename)

    def synchronize(self, time: float):
        for comp in self._components:
            comp.synchronize(time)

    def advance(self, step: float):
        self._system.advance()

        for comp in self._components:
            comp.advance(step)

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
