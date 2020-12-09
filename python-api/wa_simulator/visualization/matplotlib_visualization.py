# WA Simulator
from wa_simulator.visualization.visualization import WAVisualization

# Other imports
from math import cos, sin, ceil
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------
# WA Matplotlib Visualization
# ---------------------------

class WAMatplotlibVisualization():
    def __init__(self, vehicle, system):
        self.render_steps = int(ceil(1e-1 / system.GetStepSize()))

        self.system = system
        self.vehicle = vehicle

        self.Initialize()

    def Initialize(self):
        vp = self.vehicle.vis_properties
    
        body_Lf = vp['Body Distance to Front']
        body_Lr = vp['Body Distance to Rear']
        body_width = vp['Body Width']
        body_length = vp['Body Length']
        tire_width = vp['Tire Width']
        tire_diameter = vp['Tire Diameter']

        self.Lf = vp['Tire Distance to Front']
        self.Lr = vp['Tire Distance to Rear']
        self.track_width = vp['Track Width']
        self.wheelbase = self.Lf + self.Lr

        self.steering = 0.0
        self.throttle = 0.0
        self.braking = 0.0

        # Vehicle visualization
        cabcolor = '-k'
        wheelcolor = '-k'

        self.outline = np.array([[-body_Lr,       body_Lf,        body_Lf,         -body_Lr,        -body_Lr],
                                 [body_width / 2, body_width / 2, -body_width / 2, -body_width / 2, body_width / 2],
                                 [1,              1,                  1,           1,               1]])

        wheel = np.array([[tire_diameter, -tire_diameter, -tire_diameter, tire_diameter, tire_diameter],
                          [-tire_width,   -tire_width,    tire_width,     tire_width,    -tire_width],
                          [1,             1,              1,              1,             1]])

        self.rr_wheel = np.copy(wheel)
        self.rl_wheel = np.copy(wheel)
        self.rl_wheel[1, :] *= -1

        self.fr_wheel = np.copy(wheel)
        self.fl_wheel = np.copy(wheel)
        self.fl_wheel[1, :] *= -1

        # Initial plotting
        plt.figure(figsize=(8, 8))

        cab, = plt.plot(np.array(self.outline[0, :]).flatten(),np.array(self.outline[1, :]).flatten(), cabcolor)
        fr, = plt.plot(np.array(self.fr_wheel[0, :]).flatten(), np.array(self.fr_wheel[1, :]).flatten(), wheelcolor)
        rr, = plt.plot(np.array(self.rr_wheel[0, :]).flatten(), np.array(self.rr_wheel[1, :]).flatten(), wheelcolor)
        fl, = plt.plot(np.array(self.fl_wheel[0, :]).flatten(), np.array(self.fl_wheel[1, :]).flatten(), wheelcolor)
        rl, = plt.plot(np.array(self.rl_wheel[0, :]).flatten(), np.array(self.rl_wheel[1, :]).flatten(), wheelcolor)
        self.mat_vehicle = (cab,fr,rr,fl,rl)

        # Text
        bbox_props = dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9)
        self.annotation = plt.annotate('', xy=(.97, .7), xytext=(0, 10), xycoords=('axes fraction', 'figure fraction'), textcoords='offset points', size=10, ha='right', va='bottom',bbox=bbox_props)

        plt.xlim(-25,25)
        plt.ylim(-25,25)
        plt.gca().set_aspect('equal', adjustable='box')

    def Advance(self, step):
        if self.system.GetStepNumber() % self.render_steps == 0:
            self.Update()

            plt.pause(1e-9)

    def Synchronize(self, time, driver_inputs):
        if isinstance(driver_inputs, dict):
            s = driver_inputs["steering"]
            t = driver_inputs["throttle"]
            b = driver_inputs["braking"]
        else:
            raise TypeError('Synchronize: Type for driver inputs not recognized.')

        self.steering = s
        self.throttle = t
        self.braking = b
    
    def Transform(self, entity, x, y, yaw, alpha=0, x_offset=0, y_offset=0):
        T = np.array([[cos(yaw),  sin(yaw), x], 
                      [-sin(yaw), cos(yaw), y],
                      [0,         0,        1]])
        T = T @ np.array([[cos(alpha),  sin(alpha), x_offset], 
                          [-sin(alpha), cos(alpha), y_offset],
                          [0,         0,            1]])
        return T.dot(entity)
		
    def Update(self):
        # Update vehicle

        # State information
        x, y, yaw, v = self.vehicle.GetSimpleState()
        y *= -1
        
        fr_wheel = self.Transform(self.fr_wheel, x, y, yaw, alpha=self.steering, x_offset=self.Lf, y_offset=-self.track_width)
        fl_wheel = self.Transform(self.fl_wheel, x, y, yaw, alpha=self.steering, x_offset=self.Lf, y_offset=self.track_width)
        rr_wheel = self.Transform(self.rr_wheel, x, y, yaw, x_offset=-self.Lr, y_offset=-self.track_width)
        rl_wheel = self.Transform(self.rl_wheel, x, y, yaw, x_offset=-self.Lr, y_offset=self.track_width)
        outline = self.Transform(self.outline, x, y, yaw)

        (cab, fr, rr, fl, rl) = self.mat_vehicle
        cab.set_ydata(np.array(outline[1, :]).flatten())
        cab.set_xdata(np.array(outline[0, :]).flatten())
        fr.set_ydata(np.array(fr_wheel[1, :]).flatten())
        fr.set_xdata(np.array(fr_wheel[0, :]).flatten())
        rr.set_ydata(np.array(rr_wheel[1, :]).flatten())
        rr.set_xdata(np.array(rr_wheel[0, :]).flatten())
        fl.set_ydata(np.array(fl_wheel[1, :]).flatten())
        fl.set_xdata(np.array(fl_wheel[0, :]).flatten())
        rl.set_ydata(np.array(rl_wheel[1, :]).flatten())
        rl.set_xdata(np.array(rl_wheel[0, :]).flatten())

        # Update Text
        text = (f"Time :: {self.system.GetSimTime():.2f}\n"
                f"Steering :: {self.steering:.2f}\n"
                f"Throttle :: {self.throttle:.2f}\n"
                f"Braking :: {self.braking:.2f}\n"
                f"Speed :: {v:.2f}")
        self.annotation.set_text(text)

import signal
import sys

def signal_handler(sig, frame):
    print('Ctrl+C Detected! Exitting...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)