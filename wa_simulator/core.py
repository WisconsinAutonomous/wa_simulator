"""
Wisconsin Autonomous - https://wa.wisc.edu

Copyright (c) 2021 wa.wisc.edu
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

import argparse
from pyrr import Vector3, Quaternion
from numbers import Number
import math

# ---------
# Constants
# ---------

WA_GRAVITY = 9.81  # [m/s^2]
"""Gravitational constant (m/s^2)"""

WA_EARTH_RADIUS = 6371000.0  # [m]
"""Radius of the earth (m)"""

WA_PI = 3.141592653589793
"""PI"""

# ---------------------------------
# Vector/Quaternion/Math core items
# ---------------------------------


class WAVector(Vector3):
    """Vector object that contains x,y,z values

    This vector inherits directly from |Vector3|_, which is in the `Pyrr <https://pyrr.readthedocs.io/en/latest/index.html>`_ package. 
    The only purpose to having this class at all is purely semantic; most other classes in this simulator are prefixed with 
    `WA`, so it was desired to the same with this class. No additional functionality is added.

    .. highlight:: python
    .. code-block:: python

        # Example uses

        from wa_simulator import WAVector

        # Simple instantiation
        v1 = WAVector()
        v2 = WAVector([2, 1, 4])
        print(v1) # -> [0., 0., 0.]
        print(v2) # -> [2., 1., 4.]

        # Grab values
        print(v1.x) # -> 0.0
        print(v2.z) # -> 4.0
        print(v2[1]) # -> 1.0

        # Simple math
        v3 = WAVector([1., 1., 1.])
        print(v2 + v3) # -> [3., 2., 5.]
        print(v2 - v3) # -> [1., 0., 3.]

        # Dot product
        print(v2 * v3) # -> 7.0

        # Cross product
        print(v2 ^ v3) # -> [-3., 2., 1.]

        # Get the length
        print(v3.length) # -> 1.732

        # Normalize a vector
        v3.normalize()
        print(v3) # -> [.5773, .5773, .5773]
        print(v3.length) # -> 1.


    Please refer to the Pyrr documentation for a more detailed explaination of |Vector3|_.

    .. |Vector3| replace:: :code:`pyrr.Vector3`
    .. _Vector3: https://pyrr.readthedocs.io/en/latest/oo_api_vector.html#module-pyrr.objects.vector3
    """

    def __new__(cls, value=None, dtype=None):
        """Will construct a new :class:`~WAVector`, but change the type to float if no dtype is passed"""
        if dtype is not None:
            return super().__new__(cls, value, dtype)
        else:
            if value is not None:
                value = [float(v) for v in value]
            return super().__new__(cls, value, float)


class WAQuaternion(Quaternion):
    """Quaternion object that contains x,y,z,w values

    This quaternion class inherits directly from |Quaternion|_, which is in the `Pyrr <https://pyrr.readthedocs.io/en/latest/index.html>`_ package. 
    The only purpose to having this class at all is purely semantic; most other classes in this simulator are prefixed with 
    `WA`, so it was desired to the same with this class. Minimal additional functionality is added.

    Quaternions are rather uncommon outside of the robotics community, so a short explanation about their purpose is provided here.
    For additional information, please refer to 
    `this <https://www.allaboutcircuits.com/technical-articles/dont-get-lost-in-deep-space-understanding-quaternions/>`_ 
    and `this <https://en.wikipedia.org/wiki/Quaternion>`_.

    Quaternions are essentially mathematical operators that rotate and scale vectors. In 2D dimensional space, it's fairly likely
    you've used complex numbers to rotate vectors. For example, you may know that if you multiply a vector by the complex
    number :code:`i`, you will rotate that vector by 90 degrees. Furthermore, in 2D, to rotate any vector, you need two values: one real
    and one complex. This is, in a way, very similar to quaternions. In essence, 
    to provide the ability to rotate a vector in any desired way, you actually need four values. This is a bit counterintuitive,
    but the reasoning is outside the scope of this description (see `this video <https://www.youtube.com/watch?v=3BR8tK-LuB0>`_ 
    if you're interested). As opposed to a rotation vector in 2D, the 3D rotation vector, a quaternion, has one real and three complex
    values. These complex values, of which you've probably seen before, are named i, j and k. The real value is commonly refered to
    as w. To now rotate a 3D vector in any direction, a quaternion and it's conjugate (the original quaternion but with the opposite 
    rotation) is applied. Quaternion's rotations can be accumulated by simply "crossing" their values.

    Many have heard or used `Euler angles <https://en.wikipedia.org/wiki/Euler_angles>`_ instead. These are far more intuitive
    than quaternions, but are prone to "bugs", like `gimbal lock <https://en.wikipedia.org/wiki/Gimbal_lock>`_.

    .. highlight:: python
    .. code-block:: python

        # Example uses

        from wa_simulator import WAQuaternion, WAVector, WA_PI

        # Simple instantiation
        q1 = WAQuaternion()
        q2 = WAQuaternion([2, 1, 4, 1])
        q3 = WAQuaternion.from_z_rotation(WA_PI / 2)
        print(q1) # -> [0., 0., 0., 1.]
        print(q2) # -> [2., 1., 4., 1.]
        print(q3) # -> [0., 0., 0.70711, 0.70711]

        # Grab values
        print(q1.x) # -> 0.0
        print(q2.z) # -> 4.0
        print(q3[2]) # -> 0.70711

        # Accumulating quaternion rotations
        q4 = WAQuaternion.from_x_rotation(WA_PI)
        q5 = q3 * q4 # represents 90 degree rotation about the z, then 180 degree about the x
        print(q5) # -> [0.70711, 0.70711, 0., 0.]

        # Rotate a vector
        v = WAVector([0, 1, 0])
        print(q5 * v) # -> [1., 0., 0.]

        # Undo a rotation
        v2 = q5 * v
        print(~q5 * v2) # -> [0., 1., 0.]

        # Grab the yaw
        print(q3.to_euler_yaw()) # -> 1.57

    Please refer to the Pyrr documentation for a more detailed explaination of |Quaternion|_.

    .. |Quaternion| replace:: :code:`pyrr.Quaternion`
    .. _Quaternion: https://pyrr.readthedocs.io/en/latest/oo_api_quaternion.html#id1
    """
    def __new__(cls, value=None, dtype=None):
        """Will construct a new :class:`~WAVector`, but change the type to float if no dtype is passed"""
        if dtype is not None:
            return super().__new__(cls, value, dtype)
        else:
            if value is not None:
                value = [float(v) for v in value]
            return super().__new__(cls, value, float)

    def to_euler_roll(self) -> float:
        """Converts this quaternion to euler angles and returns the roll value (see `here <https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles>`_).

        Returns:
            float: roll
        """
        sinr_cosp = 2 * (self.w * self.x + self.y * self.z)
        cosr_cosp = 1 - 2 * (self.x * self.x + self.y * self.y)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        return roll

    def to_euler_pitch(self) -> float:
        """Converts this quaternion to euler angles and returns the pitch value (see `here <https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles>`_)

        Returns:
            float: pitch
        """
        sinp = 2 * (self.w * self.y - self.z * self.x)
        pitch = math.copysign(math.pi / 2, sinp) if abs(sinp) >= 1 else math.asin(sinp)  # noqa

        return pitch

    def to_euler_yaw(self) -> float:
        """Converts this quaternion to euler angles and returns the yaw value (see `here <https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles>`_)

        Returns:
            float: yaw
        """
        siny_cosp = 2 * (self.w * self.z + self.x * self.y)
        cosy_cosp = 1 - 2 * (self.z * self.z + self.y * self.y)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        return yaw

    def to_euler(self) -> tuple:
        """Converts this quaternion to euler angles (see `here <https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles>`_)

        Returns:
            tuple: (roll, pitch, yaw)
        """

        return self.to_euler_roll(), self.to_euler_pitch(), self.to_euler_yaw()


# --------------
# CLI core items
# --------------


class WAArgumentParser(argparse.ArgumentParser):
    """Argument parser wrapper.

    Has handy default arguments method

    .. highlight:: python
    .. code-block:: python

        # Example
        from wa_simulator import WAArgumentParser

        # Instantiate the parser and custom arguments
        parser = wa.WAArgumentParser(use_sim_defaults=True)
        parser.add_argument("-mv", "--matplotlib", action="store_true", help="Use matplotlib to visualize", default=False)
        parser.add_argument("-q", "--quiet", action="store_true", help="Silence any terminal output", default=False)

        # Parse the command line inputs
        args = parser.parse_args()

        # Grab the parsed options
        step_size = args.step_size # from default options
        render_step_size = args.render_step_size # from default options
        use_matplotlib = args.matplotlib # from default options
        is_quiet = args.quiet

    Args:
        use_sim_defaults (bool, optional): Use the default arguments (can add more). Defaults to True.
        skip_defaults (list, optional): The default arguments to skip.
        description (str, optional): Description used to describe the simulation. Printed by the help menu. Defaults to ("Wisconsin Autonomous Simulator").
    """

    def __init__(self, use_sim_defaults: bool = True, skip_defaults: list = [], description=("Wisconsin Autonomous Simulator")):
        super().__init__(description=description)

        if use_sim_defaults:
            self.add_default_sim_arguments(skip_defaults)

    def add_default_sim_arguments(self, skip_defaults: list = []):
        """Helper function to add predefined default arguments that can be used for most vehicle related simulations

        Set :code:`use_sim_defaults` in :code:`__init__` to :code:`True` to have this be called automatically.

        This function, unless specified in :code:`skip_defaults`, will add the following arguments:

        * -s, - -sim_step_size: Simulation step size
        * -rs, - -render_step_size: Rendering step size
        * -e, - -end_time: Simulation end time

        Args:
            skip_defaults (list, optional): The default arguments to skip.
        """

        def no_skip(s): return s not in skip_defaults

        if no_skip('s') and no_skip('step_size') and no_skip('sim_step_size'):
            self.add_argument(
                "-s",
                "--sim_step_size",
                type=float,
                help="Simulation Step Size [s]",
                default=3e-3,
                dest="step_size",
            )

        if no_skip('rs') and no_skip('render_step_size'):
            self.add_argument(
                "-rs",
                "--render_step_size",
                type=float,
                help="Render Update Rate [Hz]",
                default=1 / 10.0,
            )

        if no_skip('e') and no_skip('end_time'):
            self.add_argument(
                "-e",
                "--end_time",
                type=float,
                help="Simulation End Time [s]",
                default=120,
            )

        # if no_skip('r') and no_skip('record'):
        #     self.add_argument(
        #         "-r",
        #         "--record",
        #         action="store_true",
        #         help="Record Simple State Data",
        #         default=False,
        #     )
