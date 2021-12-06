"""
Wisconsin Autonomous - https://wa.wisc.edu

Copyright (c) 2021 wa.wisc.edu
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# ----------------------
# Data loading utilities
# ----------------------

import logging
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

def _file_exists(filename: str, throw_error: bool = False) -> bool:
    """
    Check if the passed filename is an actual file

    Args:
        filename (str): The filename to check
        throw_error (bool): If True, will throw an error if the file doesn't exist. Defaults to False.

    Returns:
        bool: True if the file exists, false otherwise

    Throws:
        FileNotFoundError: If filename is not a file and throw_error is set to true    
    """
    is_file = pathlib.Path(filename).is_file()
    if throw_error and not is_file:
        raise FileNotFoundError(f"{filename} is not a file.")
    return is_file


def _get_filetype(filename: str, **kwargs) -> str:
    """
    Get the filetype using the magic library.

    Args:
        filename (str): The filename to check
        kwargs (dict): Additional keyed parameters to the `from_file` method

    Returns:
        str: The file type. See libmagic documentation for supported types.
    """
    try:
        import magic
    except ImportError as e:
        LOGGER.fatal(e)
        exit()
    return magic.from_file(filename, **kwargs)


def _get_file_extension(filename: str) -> str:
    """
    Get the extension for a file

    Args:
        filename (str): The file to get the extension for

    Returns:
        str: The file extension
    """
    return pathlib.Path(filename).suffix


def _read_text(filename: str) -> str:
    """
    Read a file and return the text inside that file as a string

    Args:
        filename (str): The file to read

    Returns:
        str: The text inside filename
    """
    return pathlib.Path(filename).read_text()

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
        raise ValueError(
            f"_check_field: was expecting '{value}' for '{field}', but got '{j[field]}'.")

    if field_type is not None and not isinstance(j[field], field_type):
        raise TypeError(
            f"_check_field: was expecting '{field}' to be '{field_type}', but was '{type(j[field])}'.")

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
        raise ValueError(
            f"_check_field_allowed_values: '{j[field]}' is not an allowed value")

# ------------------
# Data Logging Utils
# ------------------


# Create logger
LOGGER = logging.getLogger(__name__)

# Create a handler with the desired format
DEFAULT_LOGGING_FORMAT = '%(levelname)-8s :: %(module)s.%(funcName)-10s :: %(message)s'
CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setFormatter(logging.Formatter(fmt=DEFAULT_LOGGING_FORMAT))

# Set default logging levels
DEFAULT_LOGGING_LEVEL = logging.WARNING
CONSOLE_HANDLER.setLevel(logging.WARNING)
LOGGER.setLevel(DEFAULT_LOGGING_LEVEL)

# Add the handler to the logger
LOGGER.addHandler(CONSOLE_HANDLER)


def set_verbosity(verbosity: int):
    """
    Set the verbosity level for the logger.
    Default verbosity is WARNING. ``verbosity`` should be a value
    greater than 0 and less than 2 that represents how many levels below WARNING is desired.
    For instance, if ``verbosity`` is 1, the new level will be INFO because
    that is one below WARNING. If ``verbosity`` is 2, the new level is DEBUG.
    DEBUG and INFO are currently the only two implemented

    Args:
        verbosity (int): A value between 0 and 2 that represents the number of levels below WARNING that should be used when logging.
    """

    if verbosity < 0 or verbosity > 2:
        raise ValueError(
            f"Verbosity should be greater than 0 and less than 2. Got {verbosity}.")

    level = logging.WARNING - verbosity * 10
    LOGGER.setLevel(level)
    CONSOLE_HANDLER.setLevel(level)
    print(f"Verbosity has been set to {logging.getLevelName(level)}")

# -----------
# YAML Parser
# -----------

# External library imports
import yaml

class YAMLParser:
    def __init__(self, filename):
        # Do some checks first
        self._filename = filename
        if not _file_exists(filename):
            raise FileNotFoundError(f"Could not read {filename}. File does not exist.")

        # Load in the file
        LOGGER.info(f"Reading {filename} as yaml...")
        with open(filename, "r") as f:
            self._data = yaml.safe_load(f)
        LOGGER.debug(f"Read {filename} as yaml.")

    def contains(self, *args) -> bool:
        """
        Checks whether the yaml file contains a certain nested attribute

        Ex:
            ```test.yml
            test:
                one: red
                two: blue
                three: green
            ```

            parser = YAMLParser('test.yml')
            parser.contains('test', 'one')          // true
            parser.contains('test', 'four')         // false
            parser.contains('test', 'one', 'red')   // false; only will search keys
           
        Args:
            *args: A list of arguments to search in the file

        Returns:
            bool: Whether the nested attributes are contained in the file
        """
        LOGGER.debug(f"Checking if {self._filename} contains nested attributes: {args}...")

        _contains = True
        temp = self._data
        for arg in args:
            if arg not in temp:
                _contains = False
                LOGGER.info(f"{self._filename} does not contain nested attributes: {args}.")
                break
            temp = temp[arg]
        return _contains

    def get(self, *args, default=None, throw_error=True) -> 'Any':
        """
        Grabs the attribute at the nested location provided by args

        Ex:
            ```test.yml
            test:
                one: red
                two: blue
                three: green
            ```

            parser = YAMLParser('test.yml')
            paresr.get('test', 'one')               // red 
            paresr.get('test', 'green', 'test')     // test
            paresr.get('test', 'green')             // raises AttributeError
           
        Args:
            *args: A list of arguments to search in the file
            default (Any): The default value if the nested attribute isn't found
            throw_error (bool): Throw an error if default is None and the attribute isn't found. Defaults to True.

        Returns:
            Any: The value at the nested attributes

        Raises:
            KeyError: If the nested attributes don't actually point to a value (i.e. contains(args) == False)
        """
        LOGGER.debug(f"Getting nested attributes from {self._filename}: {args}...")

        temp = self._data
        for arg in args:
            if arg not in temp:
                LOGGER.info(f"{self._filename} does not contain nested attributes: {args}.")
                if default is not None:
                    LOGGER.info(f"Using default: {default}.")
                temp = default
                break
            temp = temp[arg]

        if temp is None and throw_error:
            raise AttributeError(f"Default is not set and the nested attribute was not found: {args}.")

        return temp 

    def __str__(self):
        return str(self._data)

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
