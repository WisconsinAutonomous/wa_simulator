"""
Wisconsin Autonomous - https://wa.wisc.edu

Copyright (c) 2021 wa.wisc.edu
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""


from abc import abstractmethod  # Abstract Base Class

# WA Simulator
from wa_simulator.core import WAVector
from wa_simulator.utils import _load_json, _check_field, get_wa_data_file

# Other imports
import numpy as np
import matplotlib.pyplot as plt
import warnings
from scipy.interpolate import splprep, splev
from scipy.spatial.distance import cdist


def create_path_from_json(filename: str) -> 'WAPath':
    """Creates a WAPath object from json

    json file options:

    * Waypoints Input File (str, required): A csv file describing the path waypoints. Loaded using :meth:`~load_waypoints_from_csv`.

    * Additional keyworded arguments necessary for the path template

    Args:
        filename (str): The json specification that describes the path
    """

    j = _load_json(filename)

    # Validate the json file
    _check_field(j, 'Type', value='Path')
    _check_field(j, 'Template', allowed_values=['WASplinePath'])
    _check_field(j, 'Waypoints Input File', field_type=str)

    # Grab the waypoints
    waypoints_file = get_wa_data_file(j['Waypoints Input File'])
    waypoints = load_waypoints_from_csv(waypoints_file, delimiter=",")

    excluded_keys = ['Type', 'Template', 'Waypoints Input File']
    kwargs = {x: j[x] for x in j if x not in excluded_keys}

    # Create the path
    path = eval(j['Template'])(waypoints, **kwargs)

    return path


def load_waypoints_from_csv(filename: str, **kwargs) -> np.ndarray:
    r"""Get data points from a csv file.

    Should be structured as "x,y,z\\nx,y,z...". See `NumPy.loadtxt < https: // numpy.org/doc/stable/reference/generated/numpy.loadtxt.html >`_
    for more info on arguments.

    Args:
        filename(str): file to open and read data from

    Returns:
        np.ndarray: an n x m array with each data point in each row
    """
    return np.loadtxt(filename, **kwargs)


def calc_path_length_cummulative(x, y) -> np.ndarray:
    """Get the cummulative distance along a path provided the given x and y position values

    Args:
        x(np.ndarray): x coordinates
        y(np.ndarray): y coordinates

    Returns:
        np.ndarray: the cummulative distance along the path
    """
    return np.cumsum(np.linalg.norm(np.diff(np.column_stack((x, y)), axis=0), axis=1))


def calc_path_curvature(dx, dy, ddx, ddy) -> np.ndarray:
    """Calculate the curvature of a path at each point

    Args:
        dx(np.ndarray): first x derivative
        dy(np.ndarray): first y derivative
        ddx(np.ndarray): second x derivative
        ddy(np.ndarray): second y derivative

    Returns:
        np.ndarray: the curvature at each point
    """
    return (dx * ddy - dy * ddx) / (dx ** 2 + dy ** 2) ** (3 / 2)


class WAPath:
    """Base Path object. To be used to generate paths or trajectories for path planning and / or path following

    All path objects * should * be implemented in a 3D coordinate space! This means, waypoints should be a list or np.ndarray of
    lists or np.ndarrays of size 3!

    Example:

    .. highlight:: python
    .. code-block:: python

        from wa_simulator.path import WAPath, load_waypoints_from_csv

        # Simple 2D Path
        waypoints = [
            [1, 2, 0],
            [2, 2, 0],
            [5, 5, 0],
        ]
        # Not actually allowed since WAPath is abstract (has abstract methods)
        path_2D = WAPath(waypoints)

        # Simple 3D Path
        waypoints = [
            [1, 2, 1],
            [2, 2, 2],
            [5, 5, 1],
        ]
        # Not actually allowed since WAPath is abstract (has abstract methods)
        path_3D = WAPath(waypoints)

        # JSON loaded path
        waypoints = load_waypoints_from_csv("path.csv")
        # Not actually allowed since WAPath is abstract (has abstract methods)
        path_json = WAPath(waypoints)

    Args:
        waypoints(np.ndarray): The waypoints that the path interpolates about or maintains
        **kwargs: Additional keyworded arguments.

    Raises:
        TypeError: the waypoints array type is not as expected
    """

    def __init__(self, waypoints, **kwargs):
        self._parameters = kwargs

        # Check points type and shape
        if isinstance(waypoints, list):
            waypoints = np.array(waypoints)
        elif not isinstance(waypoints, np.ndarray):
            raise TypeError(
                'waypoints type is not recognized. List or NumPy array required.')

        if 3 not in waypoints.shape:
            raise ValueError(
                f'waypoints shape is {waypoints.shape}, expected (n, 3) or (3, n).')

        self._waypoints = waypoints
        self._points = waypoints
        self._d_points = None

        self._is_closed = False if 'is_closed' not in kwargs else bool(kwargs['is_closed'])
        self._vis_properties = dict() if 'vis_properties' not in kwargs else kwargs['vis_properties']

    def get_points(self, der=0) -> np.ndarray:
        """Get the points for this path

        Args:
            der(int): derivative to grab. Defaults to 0 (just the points).

        Return:
            np.ndarray: The points array

        Raises:
            ValueError: If der is not a supported value
        """
        if der == 0:
            return self._points
        elif der == 1:
            return self._d_points
        else:
            raise ValueError(f'der value of {der} is not supported.')

    def get_waypoints(self) -> np.ndarray:
        """Get the waypoints for this path

        Return:
            np.ndarray: The waypoints array
        """
        return self._waypoints

    def is_closed(self) -> bool:
        """Get whether the path is closed

        Returns:
            bool: Is the path closed?
        """
        return self._is_closed

    def get_parameters(self) -> dict:
        """Get the parameters passed in to the this function.

        Track objects essentially copy other paths, so we want to keep the parameters for later

        Returns:
            dict: The saved parameteres
        """
        return self._parameters

    def set_vis_properties(self, vis_properties: dict):
        """Set the visual properties for this path.

        The visual properties are used in :meth:`~plot`.

        Args:
            vis_properties (dict): The visual properties to apply to this path.

        Raises:
            TypeError: If ``vis_properties`` is not a ``dict``
        """
        if not isinstance(vis_properties, dict):
            raise TypeError(f"'vis_properties' was expected to be a {type(dict)}, but was {type(vis_properties)}.")

        self._vis_properties = vis_properties

    def get_vis_properties(self) -> dict:
        """Get the visual properties.

        Python will return a reference since it is not a primitive type. This means that if you change any values
        in the returned properties dictionary, it will also change the instance held by this class. This can be an
        alternative method to the :meth:`~set_vis_properties`.

        Returns:
            dict: The visual properties
        """
        return self._vis_properties

    @ abstractmethod
    def calc_closest_point(self, pos: WAVector, return_idx: bool = False) -> WAVector:
        """Calculate the closest point on the path from the passed position

        Args:
            pos(WAVector): the position to find the closest point on the path to
            return_idx(bool, optional): return the index of the point with respect to the self._points array

        Returns:
            WAVector: the closest point on the path
            int(optional): the index of the point on the path
        """
        pass

    @ abstractmethod
    def plot(self, *args, show: bool = True, **kwargs):
        """Plot the path

        Args:
            *args: Positional arguments that are passed directly to the plotter
            show(bool, optional): show the plot window. Defaults to True.
            **kwargs: Keyworded arguments passed to the plotter
        """
        pass


class WASplinePath(WAPath):
    """Spline path implemented with SciPy's splprep and splev methods

    Args:
        waypoints(np.ndarray): the waypoints to fit the spline to
        num_points(int, optional): number of points to interpolate. Defaults to 100.
        smoothness(float, optional): how fit to each point the spline should be. will hit all points by default. Defaults to 0.0.
        is_closed(bool, optional): Is the path a closed loop. Defaults to False.

    Raises:
        TypeError: the waypoints array type is not as expected
    """

    def __init__(self, waypoints, **kwargs):
        # Check inputs
        allowed_args = {'num_points': 100, 'smoothness': 0.0, 'is_closed': False}  # noqa
        for key, value in allowed_args.items():
            if key in kwargs:
                value = kwargs[key]
            setattr(self, '_' + key, value)

        super().__init__(waypoints, **kwargs)

        # Check if the path is actuall closed
        if self._is_closed and not np.array_equal(waypoints[0], waypoints[-1]):
            warnings.warn(
                "is_closed has been set to True, but the first and last waypoints are not equal. Setting is_closed to False.", RuntimeWarning, stacklevel=100)
            self._is_closed = False

        # Interpolate the path
        tck, u = splprep(self._waypoints.T, s=self._smoothness, per=self._is_closed)  # noqa
        u_new = np.linspace(u.min(), u.max(), self._num_points)

        # Evaluate the interpolation to get values
        self._x, self._y, self._z = splev(u_new, tck, der=0)  # position
        self._dx, self._dy, self._dz = splev(u_new, tck, der=1)  # first derivative # noqa
        self._ddx, self._ddy, self._ddz = splev(u_new, tck, der=2)  # second derivative # noqa

        # store the points for later
        self._points = np.column_stack((self._x, self._y, self._z))
        self._d_points = np.column_stack((self._dx, self._dy, self._dz))

        # Variables for tracking path
        self._last_index = None

    def calc_closest_point(self, pos: WAVector, return_idx: bool = False) -> (WAVector, int):
        dist = cdist(self._points, [pos])
        idx, = np.argmin(dist, axis=0)

        pos = WAVector([self._x[idx], self._y[idx], self._z[idx]])
        if return_idx:
            return pos, idx
        return pos

    def plot(self, *args, show=True, ignore_vis_properties=False, **kwargs):
        """Plot the path in matplotlib.

        Args:
            args: Positional arguments passed directly to matplotlib
            show(bool, optional): show the plot window. Defaults to True.
            ignore_vis_properties (bool, optional): If True, ignore the visual properties set through :meth:`~set_vis_properties`. If False, dict passed to :meth:`~set_vis_properties` will be passed as keyworded argements to matplotlib.
            kwargs: Keyworded arguments passed directly to matplotlib.
        """
        plt.plot(self._x, self._y, *args, **self._vis_properties, **kwargs)
        if show:
            plt.show()

    def calc_length_cummulative(self) -> np.ndarray:
        """Get the cummulative distance along the path

        Returns:
            np.ndarray: Cummulative distance along the path
        """
        return calc_path_length_cummulative(self._x, self._y)

    def calc_curvature(self) -> np.ndarray:
        """Get the curvature at each point on the path

        Returns:
            np.ndarray: Curvature at each point on the path
        """
        return calc_path_curvature(self._dx, self._dy, self._ddx, self._ddy)
