"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""


from abc import ABC, abstractmethod  # Abstract Base Class

# Other imports
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev


class WAPath:
    """Base Path object. To be used to generate paths or trajectories for path planning and/or path following"""

    @abstractmethod
    def calc_closest_point(self, pos):
        """Calcualte the closest point on the path from the passed position

        Args:
            pos (wa.WAVector): the position to find the closest point on the path to

        Returns:
            wa.WAVector: the closest point on the path
        """
        pass

    @abstractmethod
    def plot(self):
        """Plot the path. Most likely plotter is matplotlib, but technically anything can be used."""
        pass


class WASplinePath(WAPath):
    def __init__(self, waypoints, num_points=100, smoothness=0.0, is_closed=True):
        # Check points type and shape
        if isinstance(waypoints, list):
            waypoints = np.array(waypoints)
        elif not isinstance(waypoints, np.array):
            raise TypeError(
                'waypoints type is not recognized. List or NumPy array required.')

        # Store the waypoints
        self.waypoints = waypoints

        # Interpolate the path
        tck, u = splprep(waypoints.T, s=smoothness, per=is_closed)
        u_new = np.linspace(u.min(), u.max(), num_points)

        self.x, self.y = splev(u_new, tck, der=0)  # interpolation
        self.dx, self.dy = splev(u_new, tck, der=1)  # first derivative
        self.ddx, self.ddy = splev(u_new, tck, der=2)  # second derivative

        # Variables for tracking path
        self.last_index = None

    def calc_closest_point(self, pos):
        """Calcualte the closest point on the path from the passed position

        Args:
            pos (wa.WAVector): the position to find the closest point on the path to

        Returns:
            wa.WAVector: the closest point on the path
        """
        pass

    def plot(self, *args, show=True, **kwargs):
        """Plot the path

        Args:
            show (bool, optional): show the plot window. Defaults to True.
        """
        plt.plot(self.x, self.y, *args, **kwargs)
        if show:
            plt.show()


class WABezierPath(WAPath):

    def __init__(self):
        pass

    def calc_closest_point(self, pos):
        """Calcualte the closest point on the path from the passed position

        Args:
            pos (wa.WAVector): the position to find the closest point on the path to

        Returns:
            wa.WAVector: the closest point on the path
        """
        pass

    def plot(self):
        """Plot the path."""
        pass
