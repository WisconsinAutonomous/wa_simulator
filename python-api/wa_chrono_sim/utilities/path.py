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
    def Create(points):
        """
        Create a path object from an array of points
        """
        pass

    @staticmethod
    def CreateFromJSON():
        """
        Create a path object from a json specification file
        """
        pass

class WACubicSplnePath(WAPath):
    """
    
    Path that is described by a cubic spline

    """
    @staticmethod
    def Create(points):
        """
        Create a path object from an array of points
        """
        pass

    @staticmethod
    def CreateFromJSON():
        """
        Create a path object from a json specification file
        """
        pass