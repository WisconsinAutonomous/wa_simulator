"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

from abc import ABC, abstractmethod  # Abstract Base Class


class WASimulation(ABC):
    def __init__(
        self,
        system,
        environment,
        vehicle,
        visualization,
        controller,
        record_filename=None,
    ):
        """A manager for a simulation. Advances and synchronizes simulation modules.

        The simulation object is used primarily for cleaning up main functions. The Run method
        should be used primarily, as the use case for this simulator is mainly for the use of the
        controllers.

        Args:
            system (WASystem): describes the simulation system
            environment (WAEnvironment): describes the simulation environment
            vehicle (WAVehicle): describes the simulation vehicle
            visualization (WAVisualization): describes the simulation visualization
            controller (WAController): describes the simulation controller
            record_filename (str, optional): the filename to store saved simulation data. Defaults to None.

        Attributes:
            system (WASystem): describes the simulation system
            environment (WAEnvironment): describes the simulation environment
            vehicle (WAVehicle): describes the simulation vehicle
            visualization (WAVisualization): describes the simulation visualization
            controller (WAController): describes the simulation controller
            record_filename (str): the filename to store saved simulation data
        """

        self.system = system
        self.environment = environment
        self.vehicle = vehicle
        self.visualization = visualization
        self.controller = controller

        self.record_filename = record_filename
        if self.record_filename:
            # Overwrite current files
            with open(self.record_filename, "w") as f:
                pass

    def Record(self, filename):
        """Save simulation state. Only saves the vehicle simple state

        Args:
            filename (str): file to append info to
        """
        with open(filename, "a+") as f:
            x, y, yaw, v = self.vehicle.GetSimpleState()
            f.write(f"{x},{y},{yaw},{v}")

    def Synchronize(self, time):
        """Synchronize each simulation module.

        Will pass information between simulation modules

        Args:
            time (double): the time to synchronize the simulation to
        """
        vehicle_inputs = self.controller.GetInputs()

        self.controller.Synchronize(time)
        self.vehicle.Synchronize(time, vehicle_inputs)
        self.environment.Synchronize(time)

        if self.visualization:
            # Will synchronize the visualization if necessary
            self.visualization.Synchronize(time, vehicle_inputs)

    def Advance(self, step):
        """Advance each simulation module.

        Args:
            step (double): the step size to update each module by
        """
        self.system.Advance()

        self.environment.Advance(step)
        self.vehicle.Advance(step)
        self.controller.Advance(step)

        if self.visualization:
            # Will advance the visualization if necessary
            self.visualization.Advance(step)

    def Run(self):
        """Run the simulation

        Can be used to clear up main functions.
        """
        while self.IsOk():
            time = self.system.GetSimTime()

            self.Synchronize(time)
            self.Advance(self.system.step_size)

            if self.record_filename:
                self.Record(self.record_filename)

    def IsOk(self):
        """Verifies the simulation is running as expected.

        Checks the visualization if it's still active. Should probably check other
        modules for any errors.

        Returns:
            bool: Whether the simulation running as expected
        """
        return self.visualization.IsOk() if self.visualization else True
