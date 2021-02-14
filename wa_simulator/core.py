"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

import argparse
from pyrr import Vector3, Quaternion
from numbers import Number

# ---------------------------------
# Vector/Quaternion/Math core items
# ---------------------------------


class WAVector(Vector3):
    def __new__(cls, value=None, dtype=None):
        if dtype is not None:
            return super().__new__(cls, value, dtype)
        else:
            return super().__new__(cls, value, float)


class WAQuaternion(Quaternion):
    def __new__(cls, value=None, dtype=None):
        if dtype is not None:
            return super().__new__(cls, value, dtype)
        else:
            return super().__new__(cls, value, float)

    def __add__(self, other):
        """Adds two quaternions or a constant"""
        if isinstance(other, WAQuaternion):
            return WAQuaternion([self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w])
        elif isinstance(other, Number):
            return WAQuaternion([self.x + other, self.y + other, self.z + other, self.w + other])

    def __sub__(self, other):
        """Subs two quaternions or a constant"""
        if isinstance(other, WAQuaternion):
            return WAQuaternion([self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w])
        elif isinstance(other, Number):
            return WAQuaternion([self.x - other, self.y - other, self.z - other, self.w - other])

    def __mul__(self, other):
        """Multiplies by a constant"""
        if isinstance(other, Number):
            return WAQuaternion([self.x * other, self.y * other, self.z * other, self.w * other])
        else:
            return super().__mul__(other)


# --------------
# CLI core items
# --------------


class WAArgumentParser(argparse.ArgumentParser):
    """Argument parser wrapper.

    Has handy default arguments method

    Args:
        use_sim_defaults (bool, optional): Use the default arguments (can add more). Defaults to True.
        skip_defaults (list, optional): The default arguments to skip.
        description (str, optional): Description used to describe the simulation. Printed by the help menu. Defaults to ("Wisconsin Autonomous Simulator").
    """

    def __init__(self, use_sim_defaults: bool = True, skip_defaults: list = [], description=("Wisconsin Autonomous Simulator")):
        super().__init__(description=description)

        if use_sim_defaults:
            self.add_default_sim_arguments(skip_defaults)

    def add_default_sim_arguments(self, skip_defaults=[]):
        """Adds default arguments for most simulations

        Args:
            skip_defaults (list, optional): The default arguments to skip.

        Includes:
            -s,--sim_step_size: Simulation step size
            -rs,--render_step_size: Rendering step size
            -iv,--irrlicht: Use irrlicht visualization
            -mv,--matplotlib: Use matplotlib visualization
            -r,--record: Record the simulation to a csv
        """
        if 's' not in skip_defaults:
            self.add_argument(
                "-s",
                "--sim_step_size",
                type=float,
                help="Simulation Step Size",
                default=3e-3,
                dest="step_size",
            )

        if 'rs' not in skip_defaults:
            self.add_argument(
                "-rs",
                "--render_step_size",
                type=float,
                help="Render Update Rate [Hz]",
                default=1 / 10.0,
            )

        if 'iv' not in skip_defaults:
            self.add_argument(
                "-iv",
                "--irrlicht",
                action="store_true",
                help="Use Irrlicht to Visualize",
                default=False,
            )

        if 'mv' not in skip_defaults:
            self.add_argument(
                "-mv",
                "--matplotlib",
                action="store_true",
                help="Use Matplotlib to Visualize",
                default=False,
            )

        if 'r' not in skip_defaults:
            self.add_argument(
                "-r",
                "--record",
                action="store_true",
                help="Record Simple State Data",
                default=False,
            )
