"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""


from abc import ABC, abstractmethod  # Abstract Base Class

# WA Simulator
from wa_simulator.path import WAPath
from wa_simulator.core import WAVector

# Other imports
import numpy as np
import matplotlib.pyplot as plt


def create_constant_width_track(center: WAPath, width: float):
    """Generates a WAConstantWidthTrack given a centerline and a constant width. Simply "walks" along path and takes the normal from the center at a distance equal to width/2

    Args:
        center (WAPath): The centerline of the track
        width (float): The constant distance between the left and right boundaries (distance between centerline and a boundary is width/2)
    """
    if center.d_points is None:
        raise ValueError(
            'create_constant_width_track: derivative of the centerline has not been initialized')

    left, right = [], []

    points = center.points

    for i in range(len(points)-1):
        ix, iy, iz = points[i]
        d_point = center.d_points[i]
        l = np.linalg.norm(d_point)
        dx = d_point[0] * width / (2 * l)
        dy = d_point[1] * width / (2 * l)
        left.append([ix - dy, iy + dx, iz])
        right.append([ix + dy, iy - dx, iz])

    def close_path_if_necessary(points): return np.array(points) if center.parameters.is_closed and not np.array_equal(
        points[0], points[-1]) else np.vstack((points, points[0]))
    left = close_path_if_necessary(left)
    right = close_path_if_necessary(right)

    # No interpolation to maintain normals
    left_path = WAPath(left, center.parameters)
    right_path = WAPath(right, center.parameters)

    return WATrack(center, left_path, right_path, extras={'width': width})


class WATrack:
    """Base Track object. Basically holds three WAPaths: centerline and two boundaries. This class provides convenience functions so that it is easier to write various track related code

    Args:
        center (WAPath): The centerline of the track.
        left (WAPath): The "left" side boundary. Side is determined by orientation from the centerline by index.
        right (WAPath): The "right" side boundary. Side is determined by orientation from the centerline by index.
        extras (dict): Extra parameters that are used for the track

    Attributes:
        center (WAPath): The centerline of the track.
        left (WAPath): The "left" side boundary. Side is determined by orientation from the centerline by index.
        right (WAPath): The "right" side boundary. Side is determined by orientation from the centerline by index.
    """

    def __init__(self, center: WAPath, left: WAPath, right: WAPath, extras: dict = {}):
        self.center = center
        self.left = left
        self.right = right

        # Will expand out the extras dictionary into class variables
        self.__dict__.update(extras)

    def inside_boundaries(self, point: WAVector):
        """Check whether the passed point is within the track boundaries

        https://stackoverflow.com/a/33155594
        """
        if not isinstance(point, WAVector):
            raise TypeError(
                f'WATrack.inside_boundary: Expects a WAVector, not a {type(point)}.')

        closest_point, idx = self.center.calc_closest_point(point)
        A, B, C = point, WAVector(self.left.points[idx]), WAVector(self.right.points[idx])  # noqa
        a, b, c = (B-C).length, (C-A).length, (A-B).length
        return a**2 + b**2 >= c**2 and a**2 + c**2 >= b**2

    def plot(self):
        """Plot the path. Most likely plotter is matplotlib, but technically anything can be used."""
        self.center.plot('k', show=False)
        self.left.plot('k', show=False)
        self.right.plot('k', show=False)

        # for pl, pr in zip(self.left.points, self.right.points):
        #     plt.plot([pl[0], pr[0]], [pl[1], pr[1]])

        plt.show()
