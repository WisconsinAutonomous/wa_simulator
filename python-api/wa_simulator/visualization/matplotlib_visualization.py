# WA Simulator
from wa_simulator.visualization.visualization import WAVisualization

# Other imports
from math import cos, sin, tan, exp, atan2, ceil
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ------------------
# WA Chrono Irrlicht
# ------------------

class WAMatplotlibVisualization():
    def __init__(self, vehicle, system):
        self.render_steps = int(ceil(system.GetRenderStepSize() / system.GetStepSize()))

        self.system = system
        self.vehicle = vehicle

        self.Initialize()

    def Initialize(self):
        self.wheelbase = 2.776
        self.offset = np.array([-4.0, 0])
        self.backtowheel = 1.0
        self.width = 1.5958
        self.length = 4.776
        self.wheel_len = 0.41
        self.wheel_width = 0.205
        self.tread = 0.7979

        self.steering = 0.0
        self.throttle = 0.0
        self.braking = 0.0

        # Vehicle visualization
        cabcolor = '-k'
        wheelcolor = '-k'

        self.outline = np.array([[-self.backtowheel, (self.length - self.backtowheel), (self.length - self.backtowheel), -self.backtowheel, -self.backtowheel],
                                [self.width / 2, self.width / 2, - self.width / 2, -self.width / 2, self.width / 2]])

        self.fr_wheel = np.array([[self.wheel_len, -self.wheel_len, -self.wheel_len, self.wheel_len, self.wheel_len],
                                    [-self.wheel_width - self.tread, -self.wheel_width - self.tread, self.wheel_width - self.tread, self.wheel_width - self.tread, -self.wheel_width - self.tread]])

        self.rr_wheel = np.copy(self.fr_wheel)

        self.fl_wheel = np.copy(self.fr_wheel)
        self.fl_wheel[1, :] *= -1
        self.rl_wheel = np.copy(self.rr_wheel)
        self.rl_wheel[1, :] *= -1

        plt.figure(figsize=(8, 5))

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
		
    def Update(self):
        # Update vehicle

        # State information
        x, y, yaw, v = self.vehicle.GetSimpleState()

        rot1 = np.array([[cos(yaw), sin(yaw)],
                            [-sin(yaw), cos(yaw)]])
        rot2 = np.array([[cos(self.steering), sin(self.steering)],
                            [-sin(self.steering), cos(self.steering)]])

        fr_wheel = (self.fr_wheel.T.dot(rot2)).T
        fl_wheel = (self.fl_wheel.T.dot(rot2)).T
        fr_wheel[0, :] += self.wheelbase
        fl_wheel[0, :] += self.wheelbase

        fr_wheel = (fr_wheel.T.dot(rot1)).T
        fl_wheel = (fl_wheel.T.dot(rot1)).T

        outline = (self.outline.T.dot(rot1)).T
        rr_wheel = (self.rr_wheel.T.dot(rot1)).T
        rl_wheel = (self.rl_wheel.T.dot(rot1)).T

        offset = (self.offset.T.dot(rot1)).T

        outline[0, :] += offset[0] + x
        outline[1, :] += offset[1] + y
        fr_wheel[0, :] += offset[0] + x
        fr_wheel[1, :] += offset[1] + y
        rr_wheel[0, :] += offset[0] + x
        rr_wheel[1, :] += offset[1] + y
        fl_wheel[0, :] += offset[0] + x
        fl_wheel[1, :] += offset[1] + y
        rl_wheel[0, :] += offset[0] + x
        rl_wheel[1, :] += offset[1] + y

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
        text = f'Time :: {self.system.GetSimTime():.2f}\nSteering :: {self.steering:.2f}\nThrottle :: {self.throttle:.2f}\nBraking :: {self.braking:.2f}\nSpeed :: {v:.2f}'
        self.annotation.set_text(text)


import signal
import sys

def signal_handler(sig, frame):
    print('Ctrl+C Detected! Exitting...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)