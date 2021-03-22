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
from wa_simulator.utils import _load_json, _check_field, get_wa_data_file, _WAStaticAttribute


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

    j = _load_json(filename)

    # Validate the json file
    _check_field(j, 'Type', value='Environment')
    _check_field(j, 'Template', allowed_values=['WASimpleEnvironment'])
    _check_field(j, 'World', field_type=dict, optional=True)
    _check_field(j, 'Objects', field_type=list, optional=True)

    environment = eval(j['Template'])()

    load_environment_from_json(environment, filename)

    return environment


def load_environment_from_json(environment: 'WAEnvironment', filename: str):
    j = _load_json(filename)

    # Validate the json file
    _check_field(j, 'Type', value='Environment')
    _check_field(j, 'Template')
    _check_field(j, 'World', field_type=dict, optional=True)
    _check_field(j, 'Objects', field_type=list, optional=True)

    if 'World' in j:
        w = j['World']

    if 'Objects' in j:
        objects = j['Objects']

        for o in objects:
            _check_field(o, 'Size', field_type=list)
            _check_field(o, 'Position', field_type=list, optional=True)
            _check_field(o, 'Color', field_type=list, optional=True)

            kwargs = {}
            kwargs['size'] = WAVector(o['Size'])
            kwargs['position'] = WAVector(o['Position'])

            if 'Color' in o:
                kwargs['color'] = WAVector(o['Color'])

            if 'Texture' in o:
                kwargs['texture'] = o['Texture']

            if 'Name' in o:
                kwargs['name'] = o['Name']

            environment.add_asset(WABody(**kwargs))

    if 'Track' in j:
        t = j['Track']

        # Validate json
        _check_field(t, 'Track Input File', field_type=str)

        track_file = t['Track Input File']
        track = create_track_from_json(get_wa_data_file(track_file), environment)

        environment.add_asset(track.center)


class WABody:
    """Base class for arbitrary objects in a simulation world that can be visualized.

    .. highlight:: python
    .. code-block:: python

        # Example usage

        from wa_simulator import WABody, WAVector

        size = WAVector()
        pos = WAVector()

        body= WABody(pos=pos, size=size)
        print(body.size, body.pos)


    Args:
        **kwargs: Keyworded arguments that are stored as attributes in this object.
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
        self._assets = list()
        self._asset_dict = dict()

    @ abstractmethod
    def synchronize(self, time: float):
        pass

    @ abstractmethod
    def advance(self, step: float):
        pass

    def is_ok(self) -> bool:
        return True

    def create_body(self, **kwargs):
        """Create a body and add it as an asset to the world. Adds the asset using :meth:`~add_asset`.

        Args:
            **kwargs: Keyworded arguments used to create the asset
        """
        self.add_asset(WABody(**kwargs))

    def add_asset(self, asset: 'Any'):
        """Add an asset to the world

        A asset holds certain attributes that may be applicable in various simulations. This method
        stores created assets in the environment object.

        Args:
            asset (Any): The asset to add.
        """
        self._assets.append(asset)
        if hasattr(asset, 'name'):
            self._asset_dict[asset.name] = asset

    def get_assets(self) -> list:
        """Returns the assets that have been attached to this environment.

        Returns:
            list: A list of the assets added through :meth:`~add_asset`.
        """
        return self._assets

    def get_asset(self, name: str) -> 'Any':
        """Get the asset with the attached name

        Args:
            name (str): The name of the asset

        Returns:
            Any: The asset with that name

        Raises:
            KeyError: If the name is not found
        """
        if name not in self._asset_dict:
            raise KeyError(f"Asset with name '{name}' was not found.")

        return self._asset_dict[name]


class WASimpleEnvironment(WAEnvironment):
    """Simple environment that doesn't have any assets within the world."""

    _EGP_ENV_MODEL_FILE = "environments/ev_grand_prix.json"

    EGP_ENV_MODEL_FILE = _WAStaticAttribute('_EGP_ENV_MODEL_FILE', get_wa_data_file)

    def __init__(self):
        super().__init__()

    def synchronize(self, time: float):
        """Synchronize the environment with the rest of the world at the specified time

        Simple environment doesn't actually do anything for now.

        Args:
            time(float): the time at which the enviornment should be synchronized to
        """
        pass

    def advance(self, step: float):
        """Advance the state of the environment

        Simple environment doesn't actually do anything for now.

        Args:
            step(float): the time step at which the enviornment should be advanced
        """
        pass
