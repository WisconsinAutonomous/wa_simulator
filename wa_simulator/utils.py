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
DATA_DIRECTORY = str(pathlib.Path(__file__).absolute().parent / "data")


def get_wa_data_file(filename):
    """Get the absolute path to the file passed

    Args:
            filename (str): file relative to the data folder to get the absolute path for

    Returns:
            str: the absolute path of the file
    """
    return str(pathlib.Path(DATA_DIRECTORY) / filename)


def set_wa_data_directory(path):
    """Set the data path

    Args:
        path (str): relative (or absolute) path where the data is stored
    """
    global DATA_DIRECTORY

    DATA_DIRECTORY = str(pathlib.Path(path).resolve())


@contextlib.contextmanager
def set_wa_data_directory_temp(path):
    """Set the data path and yield the result. Will restore old directory immediately after

    Args:
        path (str): relative (or absolute) path where the data is stored
    """
    global DATA_DIRECTORY

    OLD_DATA_DIRECTORY = f'{DATA_DIRECTORY}'
    DATA_DIRECTORY = str(pathlib.Path(path).resolve())
    yield
    DATA_DIRECTORY = OLD_DATA_DIRECTORY

# -----------------------
# Type checking utilities
# -----------------------


def check_type(obj, correct_type, variable_name, function_name):
    """Check the type of an object to verify it is the correct type

    Args:
        obj (Any): The original object to check the type of
        correct_type (Any): The type obj should be
        variable_name (str): The name of the original variable for printing
        function_name (str): The name of the calling function
    """
    if not isinstance(obj, correct_type):
        raise TypeError(
            f"{function_name}: '{variable_name}' should be a '{correct_type}' but is '{type(obj)}.")

# ----------------------
# JSON related utilities
# ----------------------


def load_json(filename: str):
    """Load a json file

    Args:
        filename (str): The file to load
    """
    import json

    with open(filename) as f:
        j = json.load(f)

    return j


def check_field(j: dict, field: str, value=None, field_type=None, allowed_values: list = None, optional: bool = False):
    """Check a field in a dict loaded from json

    Args:
        j (dict): The dictionary loaded via a json file
        field (str): The field to check
        value (Any, optional): Some value field must be
        field_type (Type, optional): The type the field must be
        allowed_values: The allowed values
        optional (bool, optional): Whether the field is optional
    """

    if field not in j:
        if optional:
            return

        raise KeyError(
            f"check_field: '{field}' is not in the passed json")

    if value is not None and j[field] != value:
        raise ValueError(
            f"check_field: was expecting '{value}' for '{field}', but got '{j[field]}'.")

    if field_type is not None and not isinstance(j[field], field_type):
        raise TypeError(
            f"check_field: was expecting '{field}' to be '{field_type}', but was '{type(j[field])}'.")

    if allowed_values is not None:
        check_field_allowed_values(j, field, allowed_values)


def check_field_allowed_values(j: dict, field: str, allowed_values: list):
    """Check a field in a dict loaded from json and check that all elements are allowed

    Args:
        j (dict): The dictionary loaded via a json file
        field (str): The field to check
        allowed_values: The allowed values
    """

    check_field(j, field)

    # Make sure each value is present in the allowed_values list
    # Ignore dicts cause those are objects, allow parsing of those separately
    if j[field] not in allowed_values and j[field] is not dict:
        raise ValueError(
            f"check_field_allowed_values: '{j[field]}' is not an allowed value")
