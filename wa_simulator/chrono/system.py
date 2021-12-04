"""
Wisconsin Autonomous - https://wa.wisc.edu

Copyright (c) 2021 wa.wisc.edu
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

    Calls an update for the Chrono dynamics each :meth:`~advance` step.

    To instantiate a WAChronoSystem, you can either pass in various parameters directly, i.e. ``WAChronoSystem(step_size, render_step_size, ...)``
    or pass a ``argparse.Namespace`` in directly. This object is what is returned from :meth:`~WAArgumentParser.parse_args`.

    .. highlight:: python
    .. code:: python

        # Usage
        from wa_simulator.chrono import WAArgumentParser, WAChronoSystem

        # Passing values directly to the system
        system = WAChronoSystem(step_size=1e-3, render_step_size=2e-3, end_time=20, contact_method="SMC")

        # Or using WAArgumentParser
        parser = WAArgumentParser(use_sim_defaults=True)
        args = parser.parse_args()

        system = WAChronoSystem(args=args)

    Args:
        step_size (double): simulation step size. Defaults to 3e-3.
        render_step_size (double, optional): render step size. Defaults to 2e-2.
        end_time (float, optional): the end time for the simulation. Defaults to 120 seconds.
        args (argparse.Namespace, optional): the output namespace from argparse (see explanation above)
        contact_method (str, optional): the contact method to use (NSC or SMC). Defaults to "NSC".

    Raises:
        TypeError: verify the contact method is a string
    """

    def __init__(self, step_size: float = 3e-3, render_step_size: float = 2e-2, end_time: float = 120, contact_method: str = "NSC", args: 'argparse.Namespace' = None):
        super().__init__(step_size, render_step_size, end_time, args)

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

        self._system = system

    def advance(self):
        """Advance the simulation.

        Will update the dynamics of the chrono simulation
        """
        self.step_number += 1
        self.time = self._system.GetChTime()

        self._system.DoStepDynamics(self.step_size)
