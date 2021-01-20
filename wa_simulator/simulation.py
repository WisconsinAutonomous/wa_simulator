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

    def record(self, filename):
        """Save simulation state. Only saves the vehicle simple state

        Args:
            filename (str): file to append info to
        """
        with open(filename, "a+") as f:
            x, y, yaw, v = self.vehicle.get_simple_state()
            f.write(f"{x},{y},{yaw},{v}")

    def synchronize(self, time):
        """Synchronize each simulation module.

        Will pass information between simulation modules

        Args:
            time (double): the time to synchronize the simulation to
        """
        vehicle_inputs = self.controller.get_inputs()

        self.controller.synchronize(time)
        self.vehicle.synchronize(time, vehicle_inputs)
        self.environment.synchronize(time)

        if self.visualization:
            # Will synchronize the visualization if necessary
            self.visualization.synchronize(time, vehicle_inputs)

    def advance(self, step):
        """Advance each simulation module.

        Args:
            step (double): the step size to update each module by
        """
        self.system.advance()

        self.environment.advance(step)
        self.vehicle.advance(step)
        self.controller.advance(step)

        if self.visualization:
            # Will advance the visualization if necessary
            self.visualization.advance(step)

    def run(self):
        """Run the simulation

        Can be used to clear up main functions.
        """
        while self.is_ok():
            time = self.system.get_sim_time()

            self.synchronize(time)
            self.advance(self.system.step_size)

            if self.record_filename:
                self.record(self.record_filename)

    def is_ok(self):
        """Verifies the simulation is running as expected.

        Checks the visualization if it's still active. Should probably check other
        modules for any errors.

        Returns:
            bool: Whether the simulation running as expected
        """
        return self.visualization.is_ok() if self.visualization else True
