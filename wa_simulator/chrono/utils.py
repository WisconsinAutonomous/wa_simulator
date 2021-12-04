"""
Wisconsin Autonomous - https://wa.wisc.edu

Copyright (c) 2021 wa.wisc.edu
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# WA Simulator
from wa_simulator.core import WAVector, WAQuaternion
from wa_simulator.utils import _check_field, get_wa_data_directory

# Chrono specific imports
import pychrono as chrono
import pychrono.vehicle as veh

# ----------------------
# Data loading utilities
# ----------------------

import pathlib
import contextlib


def _update_chrono_data_directories():
    global _DATA_DIRECTORY, _CHRONO_DATA_DIRECTORY, _CHRONO_VEH_DATA_DIRECTORY

    if not _OVERRIDE_CHRONO_DIRECTORIES and _DATA_DIRECTORY != get_wa_data_directory():
        _DATA_DIRECTORY = get_wa_data_directory()

        _CHRONO_DATA_DIRECTORY = str(pathlib.Path(_DATA_DIRECTORY) / "chrono" / " ")[:-1]
        _CHRONO_VEH_DATA_DIRECTORY = str(pathlib.Path(_DATA_DIRECTORY) / "chrono" / "vehicle" / " ")[:-1]

        # Update the chrono paths
        chrono.SetChronoDataPath(_CHRONO_DATA_DIRECTORY)
        veh.SetDataPath(_CHRONO_VEH_DATA_DIRECTORY)


def set_chrono_directories_override(override: bool):
    """Set the chrono data directories to have the passed override value.

    Normally, it is assumed that the chrono data directories are located inside wherever :meth:`~get_wa_data_directory`
    is set to. This method will change the override functionality to either continue to look in this location, or
    allow the user to override this. To override the actual directories, use :meth:`~set_chrono_data_directory` and 
    :meth:`~set_chrono_vehicle_data_directory`.

    If set to True, the current paths will remain the same, but will not change without either setting them using the
    setters or when the wa data directory is changed (which would be the case if set to False).

    Args:
        bool: Override if True, don't if False
    """
    global _OVERRIDE_CHRONO_DIRECTORIES

    _OVERRIDE_CHRONO_DIRECTORIES = override


def set_chrono_data_directory(path: str):
    """Set the chrono data directory

    Normally, it is assumed that the chrono data directory is located inside wherever :meth:`~get_wa_data_directory`
    is set to. Using this method will override that functionality and statically assign the chrono data directory.
    If you'd like to return to the overriding functionality, call :meth:`~set_chrono_data_directory_override`.

    Args:
        path (str): relative (or absolute) path where the data is stored
    """
    global _CHRONO_DATA_DIRECTORY, _OVERRIDE_CHRONO_DIRECTORIES

    _CHRONO_DATA_DIRECTORY = path
    _OVERRIDE_CHRONO_DIRECTORIES = True

    chrono.SetChronoDataPath(_CHRONO_DATA_DIRECTORY)


def set_chrono_vehicle_data_directory(path: str):
    """Set the chrono vehicle data directory

    Normally, it is assumed that the chrono vehicle data directory is located inside wherever :meth:`~get_wa_data_directory`
    is set to. Using this method will override that functionality and statically assign the chrono vehicle data directory.
    If you'd like to return to the overriding functionality, call :meth:`~set_chrono_directories_override`.

    Args:
        path (str): relative (or absolute) path where the data is stored
    """
    global _CHRONO_DATA_DIRECTORY, _OVERRIDE_CHRONO_DIRECTORIES

    _CHRONO_DATA_DIRECTORY = path
    _OVERRIDE_CHRONO_DIRECTORIES = True

    veh.SetDataPath(_CHRONO_VEH_DATA_DIRECTORY)


def get_chrono_data_file(filename: str) -> str:
    """Get the absolute path for the filename passed relative to the :data:`~CHRONO_DATA_DIRECTORY`.

    .. highlight:: python
    .. code:: python

        # Example Usage
        from wa_simulator import get_chrono_data_file

        # By default, the data directory will be set to '<installation path of wa_simulator>/data/chrono'
        path = get_chrono_data_file('test.json')

        print(path) # -> '<installation path of wa_simulator>/data/chrono/test.json'

    Args:
        filename (str): file relative to the data folder to get the absolute path for

    Returns:
        str: the absolute path of the file
    """
    _update_chrono_data_directories()
    return str(pathlib.Path(_CHRONO_DATA_DIRECTORY) / filename)


def get_chrono_vehicle_data_file(filename: str) -> str:
    """Get the absolute path for the filename passed relative to the :data:`~CHRONO_VEH_DATA_DIRECTORY`.

    .. highlight:: python
    .. code:: python

        # Example Usage
        from wa_simulator import get_chrono_vehicle_data_file

        # By default, the data directory will be set to '<installation path of wa_simulator>/data/chrono/vehicle'
        path = get_chrono_vehicle_data_file('test.json')

        print(path) # -> '<installation path of wa_simulator>/data/chrono/vehicle/test.json'

    Args:
        filename (str): file relative to the data folder to get the absolute path for

    Returns:
        str: the absolute path of the file
    """
    _update_chrono_data_directories()
    return str(pathlib.Path(_CHRONO_VEH_DATA_DIRECTORY) / filename)


# Initialze the chrono data directory to in-repo data directory
_DATA_DIRECTORY = ""
_CHRONO_DATA_DIRECTORY = ""
_CHRONO_VEH_DATA_DIRECTORY = ""
_OVERRIDE_CHRONO_DIRECTORIES = False
_update_chrono_data_directories()

# ------------------
# vector conversions
# ------------------


def ChVector_to_WAVector(vector: chrono.ChVectorD):
    """Converts a ChVector to a WAVector

    Args:
        vector (ChVector): The vector to convert
    """
    return WAVector([vector.x, vector.y, vector.z])


def WAVector_to_ChVector(vector: WAVector):
    """Converts a WAVector to a ChVector

    Args:
        vector (WAVector): The vector to convert
    """
    return chrono.ChVectorD(vector.x, vector.y, vector.z)


def ChQuaternion_to_WAQuaternion(quaternion: chrono.ChQuaternionD):
    """Converts a ChQuaternion to a WAQuaternion

    Args:
        quaternion (ChQuaternion): The quaternion to convert
    """
    return WAQuaternion([quaternion.e1, quaternion.e2, quaternion.e3, quaternion.e0])


def WAQuaternion_to_ChQuaternion(quaternion: WAQuaternion):
    """Converts a WAQuaternion to a ChQuaternion

    Args:
        quaternion (WAQuaternion): The quaternion to convert
    """
    return chrono.ChQuaternionD(quaternion.x, quaternion.y, quaternion.z, quaternion.w)

# ----------------------
# json related utilities
# ----------------------


def ChFrame_from_json(j: dict):
    """Creates a ChFrame from a json object.

    Args:
        j (dict): The json object that will be converted to a ChFrame

    Returns:
        ChFrameD: The frame created from the json object
    """

    # Validate the json file
    _check_field(j, 'Position', field_type=list)
    _check_field(j, 'Rotation', field_type=list)

    # Do the conversion
    pos = j['Position']
    rot = j['Rotation']
    return chrono.ChFrameD(chrono.ChVectorD(pos[0], pos[1], pos[2]), chrono.ChQuaternionD(rot[0], rot[1], rot[2], rot[3]))


def ChVector_from_list(l: list, vector_type=chrono.ChVectorD):
    """Creates a ChVector from a list

    Args:
        l (list): The list to convert to a ChVector
        vector_type (Type): The ChVector type to convert to
    """
    if len(l) != 3:
        raise TypeError('list must have length 3')

    return vector_type(float(l[0]), float(l[1]), float(l[2]))
