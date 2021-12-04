"""
Wisconsin Autonomous - https://wa.wisc.edu

Copyright (c) 2021 wa.wisc.edu
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""


class WASystem:
    """Used to manage simulation parameters and can be used to update simulation dynamics

    A system is used for organizational purposes almost exclusively. It is passed to other
    module classes to handle passing various attributes. Could be responsible for updating
    module dynamics depending on the underlying models.

    To instantiate a WASystem, you can either pass in various parameters directly, i.e. ``WASystem(step_size, render_step_size, ...)``
    or pass a ``argparse.Namespace`` in directly. This object is what is returned from :meth:`~WAArgumentParser.parse_args`.

    .. highlight:: python
    .. code:: python

        # Usage
        from wa_simulator import WAArgumentParser, WASystem

        # Passing values directly to the system
        system = WASystem(step_size=1e-3, render_step_size=2e-3, end_time=20)

        # Or using WAArgumentParser
        parser = WAArgumentParser(use_sim_defaults=True)
        args = parser.parse_args()

        system = WASystem(args=args)

    Args:
        step_size (float, optional): the step size for the simulation. Defaults to 5e-2.
        render_step_size (float, optional): Render step size. Defaults to 2e-2.
        end_time (float, optional): the end time for the simulation. Defaults to 120 seconds.
        args (argparse.Namespace, optional): the output namespace from argparse (see explanation above)

    Attributes:
        step_number (int): Counter of the Advance function
        step_size (float): the step size for the simulation
        render_step_size (float): the render step size
        end_time (float): the end time for the simulation
        time (float): stores the time from the simulation
    """

    def __init__(self, step_size: float = 5e-2, render_step_size: float = 2e-2, end_time: float = 120, args: 'argparse.Namespace' = None):

        if args is not None:
            if not all(hasattr(args, attr) for attr in ['step_size', 'render_step_size', 'end_time']):
                raise AttributeError(f"'args' must have 'step_size', 'render_step_size' and 'end_time' members.")
            self.step_size = args.step_size
            self.render_step_size = args.render_step_size
            self.end_time = args.end_time
        else:
            self.step_size = step_size
            self.render_step_size = render_step_size
            self.end_time = end_time

        self.time = 0
        self.step_number = 0

    def advance(self):
        """Advance the system

        Will update the time and increment the step number
        """
        self.time += self.step_size
        self.step_number += 1

    def is_ok(self) -> bool:
        """Check whether the system is still running correctly.

        Simply verifies the end time for the simulation hasn't been reached
        """
        return self.end_time > self.time
