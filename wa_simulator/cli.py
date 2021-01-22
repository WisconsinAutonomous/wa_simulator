"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

import argparse


class WAArgumentParser(argparse.ArgumentParser):
    def __init__(
        self, use_sim_defaults=True, description=("Wisconsin Autonomous Simulator")
    ):
        """Argument parser wrapper.

        Has handy default arguments method

        Args:
            use_sim_defaults (bool, optional): Use the default arguments (can add more). Defaults to True.
            description (str, optional): Description used to describe the simulation. Printed by the help menu. Defaults to ("Wisconsin Autonomous Simulator").
        """
        super().__init__(description=description)

        if use_sim_defaults:
            self.add_default_sim_arguments()

    def add_default_sim_arguments(self):
        """Adds default arguments for most simulations

        Includes:
            -s,--sim_step_size: Simulation step size
            -rs,--render_step_size: Rendering step size
            -iv,--irrlicht: Use irrlicht visualization
            -mv,--matplotlib: Use matplotlib visualization
            -r,--record: Record the simulation to a csv
        """
        self.add_argument(
            "-s",
            "--sim_step_size",
            type=float,
            help="Simulation Step Size",
            default=3e-3,
            dest="step_size",
        )

        # Visualization
        self.add_argument(
            "-rs",
            "--render_step_size",
            type=float,
            help="Render Update Rate [Hz]",
            default=1 / 10.0,
        )
        self.add_argument(
            "-iv",
            "--irrlicht",
            action="store_true",
            help="Use Irrlicht to Visualize",
            default=False,
        )
        self.add_argument(
            "-mv",
            "--matplotlib",
            action="store_true",
            help="Use Matplotlib to Visualize",
            default=False,
        )

        self.add_argument(
            "-r",
            "--record",
            action="store_true",
            help="Record Simple State Data",
            default=False,
        )
