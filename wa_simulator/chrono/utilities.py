"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# Chrono specific imports
import pychrono as chrono


def str_list_to_ChVectorF(l: list[str]):
    if len(l) != 3:
        raise TypeError('list must have length 3')

    if any([not isinstance(item, str) for item in l]):
        raise TypeError('list should have str items')

    return chrono.ChVectorF(float(l[0]), float(l[1]), float(l[2]))
