"""
Wisconsin Autonomous - https://wa.wisc.edu

Copyright (c) 2021 wa.wisc.edu
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""


# WA Simulator
from wa_simulator.path import WAPath, create_path_from_json
from wa_simulator.core import WAVector
from wa_simulator.utils import _load_json, _check_field, get_wa_data_file

# Other imports
import numpy as np
import matplotlib.pyplot as plt


def create_track_from_json(filename: str, environment: 'WAEnvironment' = None) -> 'WATrack':
    """Creates a WATrack object from a json specification file

    json file options:

    * Center Input File (``str``, required): A json file describing the centerline. Loaded using :meth:`~create_path_from_json`

    * Width (``float``, required): The constant width between the left and right boundaries of the track.

    * Visualization (``dict``, optional): Additional visualization properties.

      * Center/Right/Left (``dict``, optional): The each paths visualization properties

        * Color (``list``, optional): Visualization color.

        * Object (``dict``, optional): An object that is placed along the path. Only parsed if ``environment`` is set.

          * Size (``list``, optional): Size of the objects.

          * Color (``list``, optional): Color of the objects.

          * Color #1 (``list``, optional): Color of an alternating set of objects. Must come with Color #2 and without Color.

          * Color #2 (``list``, optional): Color of an alternating set of objects. Must come with Color #1 and without Color.

          * Mode (``str``, optional): The mode for the object placement along the path. Options include 'Solid', 'Dashed' (3[m] separation) and 'Spread' (6[m] separation).

    .. todo::

        Add a variable width loader

    Args:
        filename (str): The json specification that describes the track 
        environment (WAEnvironment, optional): Adds objects to the environment, if present. Defaults to None (doesn't parse objects).

    Returns:
        WATrack: The created track
    """

    j = _load_json(filename)

    # Validate the json file
    _check_field(j, 'Type', value='Track')
    _check_field(j, 'Template', allowed_values='Constant Width Track')
    _check_field(j, 'Center Input File', field_type=str)
    _check_field(j, 'Width', field_type=float)
    _check_field(j, 'Visualization', field_type=dict, optional=True)

    # Create the centerline path
    center_file = get_wa_data_file(j['Center Input File'])
    center = create_path_from_json(center_file)

    width = j['Width']

    # Create the track
    track = create_constant_width_track(center, width)

    # Load the visualization, if present
    if 'Visualization' in j:
        v = j['Visualization']
        _check_field(v, 'Center', field_type=dict, optional=True)
        _check_field(v, 'Left', field_type=dict, optional=True)
        _check_field(v, 'Right', field_type=dict, optional=True)

        def _load_vis(path, path_name):
            if path_name in v:
                p = v[path_name]

                _check_field(p, 'Color', field_type=list, optional=True)
                _check_field(p, 'Object', field_type=dict, optional=True)

                if 'Color' in p:
                    path.get_vis_properties()['color'] = WAVector(p['Color'])

                if 'Object' in p and environment is not None:
                    o = p['Object']

                    _check_field(o, 'Size', field_type=list)
                    _check_field(o, 'Color', field_type=list, optional=True)
                    _check_field(o, 'Mode', field_type=str, optional=True)

                    kwargs = {}
                    kwargs['size'] = WAVector(o['Size'])

                    if 'Color' in o:
                        kwargs['color'] = WAVector(o['Color'])

                        if 'Color #1' in o or 'Color #2' in o:
                            raise ValueError("'Color' cannot be used with 'Color #1' or 'Color #2'")
                    elif 'Color #1' in o and 'Color #2' in o:
                        kwargs['color1'] = WAVector(o['Color #1'])
                        kwargs['color2'] = WAVector(o['Color #2'])
                    elif 'Color #1' in o or 'Color #2' in o:
                        raise ValueError("'Color #1' and 'Color #2' must be used together.")

                    s = path.calc_length_cummulative()[-1]
                    size = WAVector(o['Size'])
                    if 'Mode' in o:
                        m = o['Mode']

                        if m == 'Continuous':
                            n = s / size.y
                        elif m == 'Dashed':
                            n = s / 3  # Spaced as dashed center lines are (3[m] apart)
                        elif m == 'Spread':
                            n = s / 6
                        else:
                            raise ValueError(f"'{m}' is not a supported road marker type")
                    else:
                        # Defaults to continuous
                        n = s / size.y

                    points = path.get_points()
                    d_points = path.get_points(der=1)

                    s = path.calc_length_cummulative()[-1]
                    size = WAVector(o['Size'])

                    l = len(points)
                    for e, i in enumerate(range(0, l, 1 if l < n else int(l / n))):
                        p = points[i]
                        dp = d_points[i]

                        kwargs['position'] = WAVector(p)
                        kwargs['yaw'] = -np.arctan2(dp[1], dp[0])

                        if 'color1' in kwargs:
                            if e % 2 == 0:
                                kwargs['color'] = kwargs['color1']
                            else:
                                kwargs['color'] = kwargs['color2']

                        environment.create_body(**kwargs)

        _load_vis(track.center, 'Center')
        _load_vis(track.right, 'Right')
        _load_vis(track.left, 'Left')

    return track


def create_constant_width_track(center: WAPath, width: float) -> 'WATrack':
    """Generates a WAConstantWidthTrack given a centerline and a constant width. Simply "walks" along path and takes the normal from the center at a distance equal to width/2

    Args:
        center (WAPath): The centerline of the track
        width (float): The constant distance between the left and right boundaries(distance between centerline and a boundary is width/2)

    Returns:
        WATrack: The created track
    """
    if center._d_points is None:
        raise ValueError(
            'create_constant_width_track: derivative of the centerline has not been initialized')

    left, right = [], []

    points = center._points
    d_points = center._d_points

    for i in range(len(points)-1):
        ix, iy, iz = points[i]
        d_point = d_points[i]

        l = np.linalg.norm(d_point)
        dx = d_point[0] * width / (2 * l)
        dy = d_point[1] * width / (2 * l)

        left.append([ix - dy, iy + dx, iz])
        right.append([ix + dy, iy - dx, iz])

    def close_path_if_necessary(points):
        if center.is_closed() and not np.array_equal(points[0], points[-1]):
            return np.vstack((points, points[0]))
        return np.array(points)

    left = close_path_if_necessary(left)
    right = close_path_if_necessary(right)

    # No interpolation to maintain normals
    left_path = type(center)(left, **center.get_parameters())
    right_path = type(center)(right, **center.get_parameters())

    return WATrack(center, left_path, right_path, width=width)


class WATrack:
    """Base Track object. Basically holds three WAPaths: centerline and two boundaries. This class provides convenience functions so that it is easier to write various track related code

    Does *not* inherit from WABase. This is a static component, so it does not need to update.

    Args:
        center(WAPath): The centerline of the track.
        left(WAPath): The "left" side boundary. Side is determined by orientation from the centerline by index.
        right(WAPath): The "right" side boundary. Side is determined by orientation from the centerline by index.
        kwargs: Extra parameters that are used for the track

    Attributes:
        center(WAPath): The centerline of the track.
        left(WAPath): The "left" side boundary. Side is determined by orientation from the centerline by index.
        right(WAPath): The "right" side boundary. Side is determined by orientation from the centerline by index.
    """

    def __init__(self, center: WAPath, left: WAPath, right: WAPath, **kwargs):
        self.center = center
        self.left = left
        self.right = right

        # Will expand out the extras dictionary into class variables
        self.__dict__.update(kwargs)

    def inside_boundaries(self, point: WAVector) -> bool:
        """Check whether the passed point is within the track boundaries

        Implementation is explained `here <https://stackoverflow.com/a/33155594>`_.

        Args:
            point(WAVector): point to check whether it's inside the track boundaries

        Returns:
            bool: is the point inside the boundaries?
        """
        if not isinstance(point, WAVector):
            raise TypeError(
                f'WATrack.inside_boundary: Expects a WAVector, not a {type(point)}.')

        closest_point, idx = self.center.calc_closest_point(point, True)
        A, B, C = point, WAVector(self.left.get_points()[idx]), WAVector(self.right.get_points()[idx])  # noqa
        a, b, c = (B-C).length, (C-A).length, (A-B).length
        return a**2 + b**2 >= c**2 and a**2 + c**2 >= b**2

    def plot(self, show=True, center_args: dict = {}, left_args: dict = {}, right_args: dict = {}):
        """Plot the path. Most likely plotter is matplotlib, but technically anything can be used.

        Args:
            show(bool): Immediately show the plot? Defaults to True.
            center_args(dict): Keyworded parameters passed to the center plot method
            left_args(dict): Keyworded parameters passed to the left plot method
            right_args(dict): Keyworded parameters passed to the right plot method
        """
        self.center.plot(**center_args, show=False)
        self.left.plot(**left_args, show=False)
        self.right.plot(**right_args, show=False)

        if show:
            plt.show()
