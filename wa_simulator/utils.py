"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# ----------------------
# Data loading utilities
# ----------------------

import pathlib
import contextlib

# Grab the data folder in the root of this repo
_DATA_DIRECTORY = str((pathlib.Path("..") / "data").resolve())


def get_wa_data_file(filename: str) -> str:
    """Get the absolute path for the filename passed relative to the :data:`~DATA_DIRECTORY`.

    .. highlight:: python
    .. code:: python

        # Example Usage
        from wa_simulator import get_wa_data_file

        # By default, the data directory will be set to '<installation path of wa_simulator>/data'
        path = get_wa_data_file('test.json')

        print(path) # -> '<installation path of wa_simulator>/data/test.json'

    Args:
        filename (str): file relative to the data folder to get the absolute path for

    Returns:
        str: the absolute path of the file
    """
    return str(pathlib.Path(_DATA_DIRECTORY) / filename)


def get_wa_data_directory() -> str:
    """Get the data directory.

    Returns:
        str: The data directory
    """
    return _DATA_DIRECTORY


def set_wa_data_directory(path: str):
    """Set the wa data directory.

    .. highlight:: python
    .. code:: python

        # Example Usage
        from wa_simulator import set_wa_data_directory, get_wa_data_directory

        # By default, the data directory will be set to '<installation path of wa_simulator>/data'
        print(get_wa_data_directory()) # -> '<installation path of wa_simulator>/data'

        # Setting it will permenantly reset the data directory
        set_wa_data_directory('/a/random/directory')
        print(get_wa_data_directory()) # -> '/a/random/directory'

    Args:
        path (str): relative (or absolute) path where the data is stored
    """
    global _DATA_DIRECTORY

    _DATA_DIRECTORY = str(pathlib.Path(path).resolve())


@ contextlib.contextmanager
def set_wa_data_directory_temp(path: str):
    """Set wa data directory and yield the result.

    For some helper functions, :meth:`~get_wa_data_file` is called implicitly (inside the method itself).
    This method will temporarily set the data directory for a short period and return to the
    original value.

    .. highlight:: python
    .. code:: python

        # Example
        from wa_simulator import set_wa_data_directory, set_wa_data_directory_temp, create_path_from_json

        # Get the current files absolute (global) path
        from pathlib import Path
        abs_path = Path(__file__).parent.absolute()

        # By default, the data directory will be set to '<installation path of wa_simulator>/data'
        print(get_wa_data_directory()) # -> '<installation path of wa_simulator>/data'

        # Will set the data directory to this files directory
        # 'local_file.json' will be loaded from the current directory
        # create_path_from_json uses get_wa_data_file to grab a csv file, which should also be found
        # in this files current directory
        with wa.set_wa_data_directory_temp(abs_path):
            print(get_wa_data_directory()) # -> '<current location of this file>'

           path = create_path_from_json('local_file.json')

        # the data directory has been restored to its original value
        print(get_wa_data_directory()) # -> '<installation path of wa_simulator>/data'

       # The original data directory will now be reset, so 'global_file.json' should be in
       # the global data directory
       path = create_path_from_json('global_file.json')

    Args:
        path (str): relative (or absolute) path where the data is stored
    """
    global _DATA_DIRECTORY

    _OLD_DATA_DIRECTORY = f'{_DATA_DIRECTORY}'
    set_wa_data_directory(path)
    yield
    _DATA_DIRECTORY = _OLD_DATA_DIRECTORY

# -----------------------
# Type checking utilities
# -----------------------


def _check_type(obj, correct_type, variable_name: str, function_name: str):
    """Check the type of an object to verify it is the correct type

    Args:
        obj (Any): The original object to check the type of
        correct_type (Any): The type obj should be
        variable_name (str): The name of the original variable for printing
        function_name (str): The name of the calling function

    Raises:
        TypeError: if obj is not the right type
    """
    if not isinstance(obj, correct_type):
        raise TypeError(
            f"{function_name}: '{variable_name}' should be a '{correct_type}' but is '{type(obj)}.")

# ----------------------
# JSON related utilities
# ----------------------


def _load_json(filename: str) -> dict:
    """Load a json file

    Will simply use the `json library <https://docs.python.org/3/library/json.html>` and return the
    loaded dictionary.

    Args:
        filename (str): The file to load

    Returns:
        dict: The loaded json file contents in a dictionary form.
    """
    import json

    with open(filename) as f:
        j = json.load(f)

    return j


def _check_field(j: dict, field: str, value=None, field_type=None, allowed_values: list = None, optional: bool = False):
    """Check a field in a dict loaded from json

    Args:
        j (dict): The dictionary loaded via a json file
        field (str): The field to check
        value (Any, optional): Some value field must be
        field_type (Type, optional): The type the field must be
        allowed_values: The allowed values
        optional (bool, optional): Whether the field is optional

    Raises:
        KeyError: If the field is not in j
        ValueError: If the value of j[field] does not equal some value
        TypeError: If the type of j[field] is not the same as field_type
        ValueError: j[field] is not one of the allowed_values
    """

    if field not in j:
        if optional:
            return

        raise KeyError(f"_check_field: '{field}' is not in the passed json")

    if value is not None and j[field] != value:
        raise ValueError(f"_check_field: was expecting '{value}' for '{field}', but got '{j[field]}'.")

    if field_type is not None and not isinstance(j[field], field_type):
        raise TypeError(f"_check_field: was expecting '{field}' to be '{field_type}', but was '{type(j[field])}'.")

    if allowed_values is not None:
        _check_field_allowed_values(j, field, allowed_values)


def _check_field_allowed_values(j: dict, field: str, allowed_values: list):
    """Check a field in a dict loaded from json and check that all elements are allowed

    Args:
        j (dict): The dictionary loaded via a json file
        field (str): The field to check
        allowed_values: The allowed values

    Raises:
        ValueError: j[field] is not one of the allowed_values
    """

    _check_field(j, field)

    # Make sure each value is present in the allowed_values list
    # Ignore dicts cause those are objects, allow parsing of those separately
    if j[field] not in allowed_values and j[field] is not dict:
        raise ValueError(f"_check_field_allowed_values: '{j[field]}' is not an allowed value")

# ---------------------
# Private class helpers
# ---------------------


class _WAStaticAttribute:
    def __init__(self, attr, func=None):
        self._attr = attr
        self._func = func

    def __get__(self, instance, owner):
        if self._func is not None:
            return self._func(getattr(owner, self._attr))
        return getattr(owner, self._attr)
