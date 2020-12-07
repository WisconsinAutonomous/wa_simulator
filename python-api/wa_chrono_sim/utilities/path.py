import numpy as np
from scipy.interpolate import splprep, splev

class BezierPath:
    def __init__(self):
        pass

class SplinePath:
    def __init__(self, points, num_points=100, s=0.0, closed=True):
        # Store the waypoints
        self.waypoints = points

        # Interpolate the path
        tck, u = splprep(points.T, s=s, per=closed)
        u_new = np.linspace(u.min(), u.max(), num_points)

        self.x, self.y = splev(u_new, tck, der=0) # interpolation
        self.dx, self.dy = splev(u_new, tck, der=1) # first derivative
        self.ddx, self.ddy = splev(u_new, tck, der=2) # second derivative

        # Variables for tracking path
        self.last_index = None
    
    def CalcClosestPoint(self, pos):
        