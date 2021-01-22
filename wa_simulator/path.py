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
from scipy.spatial.distance import cdist


def load_waypoints_from_csv(filename, **kwargs):
    """Get data points from a csv file. 

    Should be structured as "x,y,z\nx,y,z...". See NumPy.loadtxt for more info on arguments.

    Args:
        filename (str): file to open and read data from

    Returns:
        np.ndarray: a nxm array with each data point in each row
    """
    return np.loadtxt(filename, **kwargs)


def calc_path_length_cummulative(x, y):
    """Get the cummulative distance along a path provided the given x and y position values

    Args:
        x (np.ndarray): x coordinates
        y (np.ndarray): y coordinates

    Returns:
        np.ndarray: the cummulative distance along the path
    """
    return np.cumsum(np.linalg.norm(np.diff(np.column_stack((x, y)), axis=0), axis=1))


def calc_path_curvature(dx, dy, ddx, ddy):
    """Calculate the curvature of a path at each point

    Args:
        dx (np.ndarray): first x derivative
        dy (np.ndarray): first y derivative
        ddx (np.ndarray): second x derivative
        ddy (np.ndarray): second y derivative

    Returns:
        np.ndarray: the curvature at each point
    """
    return (dx * ddy - dy * ddx) / (dx ** 2 + dy ** 2) ** (3 / 2)


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
        """Spline path implemented with SciPy's splprep and splev methods

        Args:
            waypoints (np.ndarray): the waypoints to fit the spline to
            num_points (int, optional): number of points to interpolate. Defaults to 100.
            smoothness (float, optional): how fit to each point the spline should be. will hit all points by default. Defaults to 0.0.
            is_closed (bool, optional): Is the path a closed loop. Defaults to True.

        Raises:
            TypeError: the waypoints array type is not as expected
        """
        # Check points type and shape
        if isinstance(waypoints, list):
            waypoints = np.array(waypoints)
        elif not isinstance(waypoints, np.ndarray):
            raise TypeError(
                'waypoints type is not recognized. List or NumPy array required.')

        # Store the waypoints
        self.waypoints = waypoints

        # Interpolate the path
        tck, u = splprep(waypoints.T, s=smoothness, per=is_closed)
        u_new = np.linspace(u.min(), u.max(), num_points)

        # Evaluate the interpolation to get values
        self.x, self.y = splev(u_new, tck, der=0)  # position
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
        if len(pos) == 3:
            pos = pos[:2]

        dist = cdist(np.column_stack((self.x, self.y)), [pos])
        idx, = np.argmin(dist, axis=0)
        return self.x[idx], self.y[idx], idx

    def plot(self, *args, show=True, **kwargs):
        """Plot the path

        Args:
            show (bool, optional): show the plot window. Defaults to True.
        """
        plt.plot(self.x, self.y, *args, **kwargs)
        if show:
            plt.show()

    def calc_length_cummulative(self):
        """Get the cummulative distance along the path

        Returns:
            np.ndarray: Cummulative distance along the path
        """
        return calc_path_length_cummulative(self.x, self.y)

    def calc_curvature(self):
        """Get the curvature at each point on the path

        Returns:
            np.ndarray: Curvature at each point on the path
        """
        return calc_path_curvature(self.dx, self.dy, self.ddx, self.ddy)


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
