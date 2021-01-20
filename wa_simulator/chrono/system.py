"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# WA Simulator
from wa_simulator.system import WASystem

# Chrono specific imports
import pychrono as chrono


class WAChronoSystem(WASystem):
    """Chrono system wrapper.

    Performs dynamics automatically

    Args:
        step_size (double): simulation step size
        render_step_size (double, optional): render step size. Defaults to 2e-2.
        contact_method (str, optional): the contact method to use (NSC or SMC). Defaults to "NSC".

    Raises:
        TypeError: verify the contact method is a string
    """

    def __init__(self, step_size, render_step_size=2e-2, contact_method="NSC"):
        super().__init__(step_size, render_step_size)

        if not isinstance(contact_method, str):
            raise TypeError("Contact method must be of type str")

        if contact_method == "NSC":
            system = chrono.ChSystemNSC()
        elif contact_method == "SMC":
            system = chrono.ChSystemSMC()
        system.Set_G_acc(chrono.ChVectorD(0, 0, -9.81))
        system.SetSolverType(chrono.ChSolver.Type_BARZILAIBORWEIN)
        system.SetSolverMaxIterations(150)
        system.SetMaxPenetrationRecoverySpeed(4.0)
        self.system = system

    def advance(self):
        """Advance the simulation.

        Will update the dynamics of the chrono simulation
        """
        self.step_number += 1
        self.system.DoStepDynamics(self.step_size)

    def get_sim_time(self):
        """Get the simulation time.

        Will get the time from the wrapped ChSystem

        Returns:
            double: the simulation time
        """
        self.time = self.system.GetChTime()
        return self.time