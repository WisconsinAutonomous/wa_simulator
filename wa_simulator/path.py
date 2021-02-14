"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""


from abc import ABC, abstractmethod  # Abstract Base Class

# WA Simulator
from wa_simulator.core import WAVector

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
    """Base Path object. To be used to generate paths or trajectories for path planning and/or path following

    Attributes:
        parameters (WAPath.WAPathParameters): The parameters used to interpolate along the path
        waypoints (np.ndarray): The waypoints that the path interpolates about or maintains
        points (np.ndarray): The interpolated points (can be the waypoints)
    """

    class WAPathParameters:
        """Holds the parameters for the interpolated path

        Attributes:
            is_closed (bool): Whether the path is a closed loop. Defaults to True. 
        """
        is_closed = True

    def __init__(self, waypoints=None, parameters=WAPathParameters()):
        # Check points type and shape
        if isinstance(waypoints, list):
            waypoints = np.array(waypoints)
        elif not isinstance(waypoints, np.ndarray):
            raise TypeError(
                'waypoints type is not recognized. List or NumPy array required.')

        self.waypoints = waypoints
        self.points = waypoints
        self.d_points = None

        self.parameters = parameters

    @abstractmethod
    def calc_closest_point(self, pos):
        """Calculate the closest point on the path from the passed position

        Args:
            pos (wa.WAVector): the position to find the closest point on the path to

        Returns:
            wa.WAVector: the closest point on the path
        """
        pass

    @abstractmethod
    def plot(self, *args, show=True, **kwargs):
        """Plot the path

        Args:
            show (bool, optional): show the plot window. Defaults to True.
        """
        plt.plot(self.points[:, 0], self.points[:, 1], *args, **kwargs)
        if show:
            plt.show()


class WASplinePath(WAPath):
    """Spline path implemented with SciPy's splprep and splev methods

    Args:
        waypoints (np.ndarray): the waypoints to fit the spline to
        num_points (int, optional): number of points to interpolate. Defaults to 100.
        smoothness (float, optional): how fit to each point the spline should be. will hit all points by default. Defaults to 0.0.
        is_closed (bool, optional): Is the path a closed loop. Defaults to True.

    Raises:
        TypeError: the waypoints array type is not as expected
    """

    class WASplinePathParameters(WAPath.WAPathParameters):
        """The parameters for a WASplinePath

        Attributes:
            num_points (int): number of points to interpolate along the path. Defaults to 100.
            smoothness (float): How close the path is to the waypoints. Defaults to 0.0 (goes through all the points).
        """
        num_points = 100
        smoothness = 0.0

    def __init__(self, waypoints, parameters=None, **kwargs):
        # Check inputs
        parameters = parameters if parameters is not None else self.WASplinePathParameters()
        allowed_args = {'num_points', 'smoothness', 'is_closed'}
        for key, value in kwargs.items():
            if key not in allowed_args:
                raise ValueError(
                    f'Passed argument {key} is not allowed. Must be any of the following: {allowed_args}')
            setattr(parameters, key, value)

        super().__init__(waypoints, parameters)

        # Interpolate the path
        tck, u = splprep(self.waypoints.T, s=self.parameters.smoothness,
                         per=self.parameters.is_closed)
        u_new = np.linspace(u.min(), u.max(), self.parameters.num_points)

        # Evaluate the interpolation to get values
        self.x, self.y, self.z = splev(u_new, tck, der=0)  # position
        self.dx, self.dy, self.dz = splev(u_new, tck, der=1)  # first derivative # noqa
        self.ddx, self.ddy, self.ddz = splev(u_new, tck, der=2)  # second derivative # noqa

        # store the points for later
        self.points = np.column_stack((self.x, self.y, self.z))
        self.d_points = np.column_stack((self.dx, self.dy, self.dz))

        # Variables for tracking path
        self.last_index = None

    def calc_closest_point(self, pos):
        """Calculate the closest point on the path from the passed position

        Args:
            pos (wa.WAVector): the position to find the closest point on the path to

        Returns:
            wa.WAVector: the closest point on the path
            idx: the index of the point on the path
        """
        dist = cdist(self.points, [pos])
        idx, = np.argmin(dist, axis=0)

        return WAVector([self.x[idx], self.y[idx], self.z[idx]]), idx

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
