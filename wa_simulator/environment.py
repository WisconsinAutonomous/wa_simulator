"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

from abc import abstractmethod  # Abstract Base Class

# WA Simulator
from wa_simulator.base import WABase
from wa_simulator.core import WAVector
from wa_simulator.track import create_track_from_json
from wa_simulator.utils import load_json, check_field, get_wa_data_file

# Other imports
from math import atan2


def create_environment_from_json(filename: str) -> 'WAEnvironment':
    """Loads and creates a WAEnvironment from a json specification file

    An environment handles data and assets present in the world. An environment json file
    will hold that description, such as where obstacles are placed, the current weather,
    the terrain/ground properties, etc.

    See :meth:`~load_chrono_environment_from_json` for a larger support of environment properties.

    .. todo::

        Performance really dips with larger number of points

    Args:
        filename (str): The json specification file

    Returns:
        WAEnvironment: The created environment
    """

    j = load_json(get_wa_data_file(filename))

    # Validate the json file
    check_field(j, 'Type', value='Environment')
    check_field(j, 'Template', allowed_values=['WASimpleEnvironment'])
    check_field(j, 'World', field_type=dict, optional=True)
    check_field(j, 'Objects', field_type=list, optional=True)

    environment = eval(j['Template'])()

    if 'World' in j:
        w = j['World']

    if 'Objects' in j:
        objects = j['Objects']

        for o in objects:
            check_field(o, 'Size', field_type=list)
            check_field(o, 'Position', field_type=list, optional=True)
            check_field(o, 'Color', field_type=list, optional=True)

            args = {}
            args['size'] = WAVector(o['Size'])
            args['position'] = WAVector(o['Position'])

            if 'Color' in o:
                args['color'] = WAVector(o['Color'])

            environment.add_body(WABody(args))

    if 'Track' in j:
        t = j['Track']

        # Validate json
        check_field(t, 'Track Input File', field_type=str)
        check_field(t, 'Boundary Object', field_type=dict)

        track_file = t['Track Input File']
        track = create_track_from_json(get_wa_data_file(track_file))

        o = t['Boundary Object']

        # Validate json
        check_field(o, 'Size', field_type=list)
        check_field(o, 'Color', field_type=list, optional=True)

        kwargs = {}
        kwargs['size'] = WAVector(o['Size'])

        if 'Color' in o:
            kwargs['color'] = WAVector(o['Color'])

        left_points = track.left.get_points()
        left_d_points = track.left.get_points(der=1)
        right_points = track.right.get_points()
        right_d_points = track.right.get_points(der=1)

        l = len(left_points)
        n = 50
        for i in range(0, l, 1 if l < n else int(l / n)):
            lp = left_points[i]
            ldp = left_d_points[i]
            rp = right_points[i]
            rdp = right_d_points[i]

            kwargs['position'] = WAVector(lp)
            kwargs['yaw'] = -atan2(ldp[1], ldp[0])
            environment.add_body(WABody(**kwargs))

            kwargs['position'] = WAVector(rp)
            kwargs['yaw'] = -atan2(rdp[1], rdp[0])
            environment.add_body(WABody(**kwargs))

    return environment


class WABody:
    """Base class for arbitrary objects in a simulation world

    .. highlight:: python
    .. code-block:: python

        # Example usage

        from wa_simulator import WABody, WAVector

        size = WAVector()
        pos = WAVector()

        body = WABody(pos=pos, size=size)
        print(body.size, body.pos)


    Args:
        **kwargs: Keyworded arguments that are stored as attributes in this object
    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def getattr(self, attr: str):
        """Gets the passed attr if present and returns it, returns None if it's not present

        Args:
            attr (str): The attr to get and return

        Returns:
            Any: Returns either None if attr is not present or the actual attribute
        """
        try:
            return getattr(self, attr)
        except AttributeError:
            return None


class WAEnvironment(WABase):
    """Base class for the environment object.

    The environment object is responsible for handling data or assets within the world.
    Assets may be obstacles, miscellaneous objects, other vehicles or weather.
    """

    def __init__(self):
        self._bodies = []

    @ abstractmethod
    def synchronize(self, time: float):
        pass

    @ abstractmethod
    def advance(self, step: float):
        pass

    def is_ok(self) -> bool:
        return True

    def add_body(self, body: WABody):
        """Add a body to the world

        A body holds certain attributes that may be applicable in various simulations. This method
        stores created bodies in the environment object

        Args:
            body (WABody): The body to add
        """
        self._bodies.append(body)

    def get_bodies(self) -> list:
        """Returns the bodies that have been attached to this environment

        Returns:
            list: A list of the bodies added through :meth:`~add_body`
        """
        return self._bodies


class WASimpleEnvironment(WAEnvironment):
    """Simple environment that doesn't have any assets within the world."""

    EGP_ENV_MODEL_FILE = "environments/ev_grand_prix.json"
    """evGrand Prix Environment Description"""

    def __init__(self):
        super().__init__()

    def synchronize(self, time: float):
        """Synchronize the environment with the rest of the world at the specified time

        Simple environment doesn't actually do anything for now.

        Args:
            time (float): the time at which the enviornment should be synchronized to
        """
        pass

    def advance(self, step: float):
        """Advance the state of the environment

        Simple environment doesn't actually do anything for now.

        Args:
            step (float): the time step at which the enviornment should be advanced
        """
        pass
