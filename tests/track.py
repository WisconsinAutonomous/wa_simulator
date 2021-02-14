"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

import unittest
import numpy as np

# Import the track module
from wa_simulator.core import get_wa_data_file
from wa_simulator.path import WASplinePath, load_waypoints_from_csv, calc_path_length_cummulative, calc_path_curvature
from wa_simulator.track import WATrack, create_constant_width_track

# -----
# Tests
# -----


class TestWATrack(unittest.TestCase):
    """Tests method related to the WATrack"""

    def test_create_constant_width_track(self):
        """Tests the create_constant_width_track method"""
        # Create the centerline
        filename = wa.get_wa_data_file("paths/sample_medium_loop.csv")
        points = wa.load_waypoints_from_csv(filename, delimiter=",")
        path = wa.WASplinePath(points, num_points=1000)

        # Create the track
        track = wa.create_constant_width_track(path, width=6)


if __name__ == '__main__':
    unittest.main()
