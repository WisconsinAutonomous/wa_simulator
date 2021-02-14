"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# WA Simulator
from wa_simulator.core import WAVector, WAQuaternion
from wa_simulator.utils import check_field

# Chrono specific imports
import pychrono as chrono

# ------------------
# vector conversions
# ------------------


def ChVector_to_WAVector(vector: chrono.ChVectorD):
    """Converts a ChVector to a WAVector

    Args:
        vector (ChVector): The vector to convert
    """
    return WAVector([vector.x, vector.y, vector.z])


def ChQuaternion_to_WAQuaternion(quaternion: chrono.ChQuaternionD):
    """Converts a ChQuaternion to a WAQuaternion

    Args:
        quaternion (ChQuaternion): The quaternion to convert
    """
    return WAQuaternion([quaternion.e0, quaternion.e1, quaternion.e2, quaternion.e3])

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
    check_field(j, 'Position', field_type=list)
    check_field(j, 'Rotation', field_type=list)

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
