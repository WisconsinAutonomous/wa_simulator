# ----------------------------------------------------------------------------------------
# A path class should maintain and calculate responable smoothed
# approximations of waypoints in some scenario. Varying levels
# of sophistication are necessary, but some possible options:
#   - Linear model
#   - Scipy spline
#   - Bezier Curve
#
# The path class also should contain helpful methods for many
# applications. Examples of such methods:
#   - Tracker for calculating closest point on the path
#   - Curvature at a specific point
# 
# ----------------------------------------------------------------------------------------

from __future__ import annotations
import numpy as np

class WAPath:
    def __init__(self):
        """

        """
        pass

class WAPathTracker:
    def __init__(self, path):
        pass

class WABezierPath(WAPath):
    """
    
    Path that is described by a bezier curve

    """
    @staticmethod
    def create(points: np.ndarray, in_cv = np.ndarray, out_cv = np.ndarray) -> WABezierPath:
        """
        Create a path object from an array of points
        """

        # check shape of points
        if points is not None and points.shape[1] != 1:
            raise ValueError("points must consist of the one column of ChVectorD's!")

        # check if in_cv or out_cv was passed
        use_cv = False
        if in_cv is not None and out_cv is not None:
            use_cv = True
        
        

    @staticmethod
    def create_from_file():
        """
        Create a path object from a json specification file
        """
        pass

class WACubicSplnePath(WAPath):
    """
    
    Path that is described by a cubic spline

    """
    @staticmethod
    def create(points) -> WACubicSplnePath:
        """
        Create a path object from an array of points
        """
        pass

    @staticmethod
    def create_from_json():
        """
        Create a path object from a json specification file
        """
        pass