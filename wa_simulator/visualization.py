"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

from abc import ABC, abstractmethod  # Abstract Base Class

# Other imports
from multiprocessing import Process, Queue, set_start_method
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class WAVisualization(ABC):
    """Base class to be used for visualization of the simulation world.

    Derived classes will use various world attributes to visualize the simulation
    """

    @abstractmethod
    def Synchronize(self, time, vehicle_inputs):
        """Synchronize the visualization at the specified time with the passed vehicle inputs

        Args:
            time (double): time to synchronize the visualization to
            vehicle_inputs (WAVehicleInputs): inputs to the vehicle. Can be helpful for visualization (debug) purposes.
        """
        pass

    @abstractmethod
    def Advance(self, step):
        """Advance the state of the visualization by the specified step

        Args:
            step (double): step size to update the visualization by
        """
        pass

    @abstractmethod
    def IsOk(self):
        """Verifies the visualization is running properly.

        Returns:
            bool: Whether the visualization is running correctly.
        """
        pass


class WAMatplotlibVisualization:
    """Matplotlib visualizer of the simulator world and the vehicle

    Args:
        vehicle (WAVehicle): vehicle to render in the matplotlib plot window
        system (WASystem): system used to grab certain parameters of the simulation

    Attributes:
        render_steps (int): steps between which the visualization should update
        vehicle (WAVehicle): vehicle to render in the matplotlib plot window
        system (WASystem): system used to grab certain parameters of the simulation
        Lf (double): distance between COM and front axle
        Lr (double): distance between COM and rear axle
        track_width (double): distance between wheels connected to the same axle
        wheelbase (double): distance between front and rear wheels
        steering (double): steering value
        throttle (double): throttle value
        braking (double): braking value
        time (double): time of the simulation
        outline (double): chassis outline for the vehicle that's updated based on pose of the vehicle
        rr_wheel (double): right rear wheel outline that's updated based on the pose of the body in the simulation
        rl_wheel (double): left rear wheel outline that's updated based on the pose of the body in the simulation
        fr_wheel (double): right front wheel outline that's updated based on the pose of the body in the simulation
        fl_wheel (double): left front  wheel outline that's updated based on the pose of the body in the simulation
        q (multiprocessing.Queue): Queue used to pass info between processes (thread safe)
        input_q (multiprocessing.Queue): Queue used to pass info between processes, but key press inputs (thread safe)
        plotter (VehiclePlotter): Used to update the matplotlib window
        p (multiprocessing.Process): process created by multiprocessing (TODO: Should add join())
        check_for_key_presses (bool): Whether to check VehiclePlotter for keyboard inputs
        key_input (matplotlib.backend_bases.KeyEvent): The most recent keypress from the vehicle plotter
    """

    class SimState:
        def __init__(
            self,
            outline=None,
            rr_wheel=None,
            rl_wheel=None,
            fr_wheel=None,
            fl_wheel=None,
            steering=None,
            throttle=None,
            braking=None,
            time=None,
            speed=None,
        ):
            """The simulation state. Used to store variables sent between processes.

            Args:
                outline (np.array, optional): matplotlib representation of the body. Defaults to None.
                rr_wheel (np.array, optional): matplotlib representation of the rear right wheel. Defaults to None.
                rl_wheel (np.array, optional): matplotlib representation of the rear left wheel. Defaults to None.
                fr_wheel (np.array, optional): matplotlib representation of the front right wheel. Defaults to None.
                fl_wheel (np.array, optional): matplotlib representation of the front left wheel. Defaults to None.
                steering (double, optional): steering value. Defaults to None.
                throttle (double, optional): throttle value. Defaults to None.
                braking (double, optional): braking value. Defaults to None.
                time (double, optional): time of the simulation. Defaults to None.
                speed (double, optional): speed of the vehicle. Defaults to None.
            """
            self.outline = outline
            self.rr_wheel = rr_wheel
            self.rl_wheel = rl_wheel
            self.fr_wheel = fr_wheel
            self.fl_wheel = fl_wheel
            self.steering = steering
            self.throttle = throttle
            self.braking = braking
            self.time = time
            self.speed = speed

        def Get(self):
            return (
                self.outline,
                self.rr_wheel,
                self.rl_wheel,
                self.fr_wheel,
                self.fl_wheel,
                self.steering,
                self.throttle,
                self.braking,
                self.time,
                self.speed,
            )

    class VehiclePlotter:
        """Class used to handle plotting of the vehicle.

        Runs in separate process and communicates with main thread via multiprocessing.Queue
        object. Done to improve simulation performance. Plotter will block until vehicle state has updated.
        On vehicle state update, the visualization representation is also updated.

        Instead of being redrawn, handles to matplotlib assets are stored and their states are updated
        at each visualization update. This improves performance and doesn't require clearing the plot
        window.

        Attributes:
            q (multiprocessing.Queue): Queue used to pass info between processes
            input_q (multiprocessing.Queue): Queue used to pass info between processes, but for key press inputs
            fig (plt.Figure): Matplotlib figure used for plotting
            ax (plt.Axes): Matplotlib axes used for plotting
            mat_vehicle (tuple): Class that holds the matplotlib visualization objects so their state can be updated
            annotation (plt.Text): Holds text displayed in the plot window for debug purposes.
        """

        def Initialize(self, q, input_q):
            """Initialize the matplotlib visual assets to be updated through the simulation. Initially plotted at (0,0).

            Args:
                q (multiprocessing.Queue): Queue used to communicate between processes
                input_q (multiprocessing.Queue): Queue used to communicate between processes, but for key press inputs
            """
            self.q = q
            self.input_q = input_q

            cabcolor = "-k"
            wheelcolor = "-k"

            out = self.q.get()
            if not isinstance(out, WAMatplotlibVisualization.SimState):
                raise TypeError("Out is not a SimState")

            (
                outline,
                rr_wheel,
                rl_wheel,
                fr_wheel,
                fl_wheel,
                steering,
                throttle,
                braking,
                time,
                speed,
            ) = out.Get()

            # Initial plotting setup
            self.fig, self.ax = plt.subplots(figsize=(8, 8))

            (cab,) = self.ax.plot(
                np.array(outline[0, :]).flatten(),
                np.array(outline[1, :]).flatten(),
                cabcolor,
            )
            (fr,) = self.ax.plot(
                np.array(fr_wheel[0, :]).flatten(),
                np.array(fr_wheel[1, :]).flatten(),
                wheelcolor,
            )
            (rr,) = self.ax.plot(
                np.array(rr_wheel[0, :]).flatten(),
                np.array(rr_wheel[1, :]).flatten(),
                wheelcolor,
            )
            (fl,) = self.ax.plot(
                np.array(fl_wheel[0, :]).flatten(),
                np.array(fl_wheel[1, :]).flatten(),
                wheelcolor,
            )
            (rl,) = self.ax.plot(
                np.array(rl_wheel[0, :]).flatten(),
                np.array(rl_wheel[1, :]).flatten(),
                wheelcolor,
            )
            self.mat_vehicle = (cab, fr, rr, fl, rl)

            # Text
            bbox_props = dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9)
            self.annotation = self.ax.annotate(
                "",
                xy=(0.97, 0.7),
                xytext=(0, 10),
                xycoords=("axes fraction", "figure fraction"),
                textcoords="offset points",
                size=10,
                ha="right",
                va="bottom",
                bbox=bbox_props,
            )

            # Plot styling
            self.ax.set_xlim(-25, 25)
            self.ax.set_ylim(-25, 25)
            self.ax.set_aspect("equal", adjustable="box")

        def KeyPress(self, event):
            if self.input_q.full():
                self.input_q.get()
            self.input_q.put(event.key)

        def Update(self, i):
            """Update the state of the vehicle in the visualization

            Called at specific intervals by the FuncAnimation function in matplotlib

            Args:
                i (int): frame number
            """
            (cab, fr, rr, fl, rl) = self.mat_vehicle

            out = self.q.get()
            if isinstance(out, bool):
                self.fig.canvas.mpl_connect("key_press_event", self.KeyPress)
                self.event = True
                return
            elif not isinstance(out, WAMatplotlibVisualization.SimState):
                raise TypeError("Out is not a SimState")

            (
                outline,
                rr_wheel,
                rl_wheel,
                fr_wheel,
                fl_wheel,
                steering,
                throttle,
                braking,
                time,
                speed,
            ) = out.Get()

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
            text = (
                f"Time :: {time:.2f}\n"
                f"Steering :: {steering:.2f}\n"
                f"Throttle :: {throttle:.2f}\n"
                f"Braking :: {braking:.2f}\n"
                f"Speed :: {speed:.2f}"
            )
            self.annotation.set_text(text)

        def Plot(self, q, input_q):
            """ "Main" function that sets up the plotter and runs the blocking FuncAnimation update.

            Args:
                q (multiprocessing.Queue): Queue used to communicate and pass info between processes
                input_q (multiprocessing.Queue): Queue used to communicate and pass info between processes, but for key presses
            """
            self.Initialize(q, input_q)

            anim = FuncAnimation(self.fig, self.Update, interval=10)

            plt.show()

    def __init__(self, vehicle, system):
        self.render_steps = int(np.ceil(system.render_step_size / system.step_size))

        self.system = system
        self.vehicle = vehicle

        properties = self.vehicle.vis_properties

        body_Lf = properties["Body Distance to Front"]
        body_Lr = properties["Body Distance to Rear"]
        body_width = properties["Body Width"]
        body_length = properties["Body Length"]
        tire_width = properties["Tire Width"]
        tire_diameter = properties["Tire Diameter"]

        self.Lf = properties["Tire Distance to Front"]
        self.Lr = properties["Tire Distance to Rear"]
        self.track_width = properties["Track Width"]
        self.wheelbase = self.Lf + self.Lr

        self.steering = 0.0
        self.throttle = 0.0
        self.braking = 0.0
        self.time = 0.0

        # Visualization shapes
        self.outline = np.array(
            [
                [-body_Lr, body_Lf, body_Lf, -body_Lr, -body_Lr],
                [
                    body_width / 2,
                    body_width / 2,
                    -body_width / 2,
                    -body_width / 2,
                    body_width / 2,
                ],
                [1, 1, 1, 1, 1],
            ]
        )

        wheel = np.array(
            [
                [
                    tire_diameter,
                    -tire_diameter,
                    -tire_diameter,
                    tire_diameter,
                    tire_diameter,
                ],
                [-tire_width, -tire_width, tire_width, tire_width, -tire_width],
                [1, 1, 1, 1, 1],
            ]
        )

        self.rr_wheel = np.copy(wheel)
        self.rl_wheel = np.copy(wheel)
        self.rl_wheel[1, :] *= -1

        self.fr_wheel = np.copy(wheel)
        self.fl_wheel = np.copy(wheel)
        self.fl_wheel[1, :] *= -1

        # Initialize multiprocessed animation
        if plt.get_backend() == "MacOSX":
            set_start_method("spawn", force=True)

        self.q = Queue(maxsize=1)
        self.input_q = Queue(maxsize=1)

        self.plotter = self.VehiclePlotter()
        self.p = Process(target=self.plotter.Plot, args=(self.q, self.input_q))
        self.p.start()

        self.q.put(
            self.SimState(
                self.outline,
                self.rr_wheel,
                self.rl_wheel,
                self.fr_wheel,
                self.fl_wheel,
                self.steering,
                self.throttle,
                self.braking,
                self.time,
                0,
            )
        )

        # Don't check for key presses as a default
        self.check_for_key_presses = False
        self.key_input = None

    def Synchronize(self, time, vehicle_inputs):
        """Synchronize the vehicle inputs to the values in this visualization

        Will just set class members

        Args:
            time (double): time at which to update the vehicle to
            vehicle_inputs (WAVehicleInputs): vehicle inputs
        """
        self.steering = vehicle_inputs.steering
        self.throttle = vehicle_inputs.throttle
        self.braking = vehicle_inputs.braking

        self.time = time

    def Advance(self, step):
        """Advance the state of the visualization by the specified step

        Will only call update if the scene should be rendered given the render step

        Args:
            step (double): step size to update the visualization by
        """
        if self.system.GetStepNumber() % self.render_steps == 0:
            self.Update()

            if self.check_for_key_presses and self.input_q.full():
                self.key_input = self.input_q.get()

    def Transform(self, entity, x, y, yaw, alpha=0, x_offset=0, y_offset=0):
        """Helper function to transfrom a numpy entity by the specified values

        Args:
            entity (np.array): Numpy entity that describes some visualization asset to be updated
            x (double): x translation distance
            y (double): y translation distance
            yaw (double): angle to rotate by
            alpha (double, optional): angle to rotate by to be added after the rotation. Defaults to 0.
            x_offset (double, optional): x translation distance to be added after the rotation. Defaults to 0.
            y_offset (double, optional): y translation distance to be added after the rotation. Defaults to 0.

        Returns:
            np.array: the new entity
        """
        T = np.array(
            [[np.cos(yaw), np.sin(yaw), x], [-np.sin(yaw), np.cos(yaw), y], [0, 0, 1]]
        )
        T = T @ np.array(
            [
                [np.cos(alpha), np.sin(alpha), x_offset],
                [-np.sin(alpha), np.cos(alpha), y_offset],
                [0, 0, 1],
            ]
        )
        return T.dot(entity)

    def Update(self):
        """Update the state of the vehicle representation.

        After updating, will push the state to the queue to be read by the VehiclePlotter
        """

        # State information
        x, y, yaw, v = self.vehicle.GetSimpleState()
        y *= -1

        fr_wheel = self.Transform(
            self.fr_wheel,
            x,
            y,
            yaw,
            alpha=self.steering,
            x_offset=self.Lf,
            y_offset=-self.track_width,
        )
        fl_wheel = self.Transform(
            self.fl_wheel,
            x,
            y,
            yaw,
            alpha=self.steering,
            x_offset=self.Lf,
            y_offset=self.track_width,
        )
        rr_wheel = self.Transform(
            self.rr_wheel, x, y, yaw, x_offset=-self.Lr, y_offset=-self.track_width
        )
        rl_wheel = self.Transform(
            self.rl_wheel, x, y, yaw, x_offset=-self.Lr, y_offset=self.track_width
        )
        outline = self.Transform(self.outline, x, y, yaw)
        time = self.system.GetSimTime()

        # Update plotter driver inputs
        steering = self.steering
        throttle = self.throttle
        braking = self.braking

        self.q.put(
            self.SimState(
                outline,
                rr_wheel,
                rl_wheel,
                fr_wheel,
                fl_wheel,
                self.steering,
                self.throttle,
                self.braking,
                self.time,
                v,
            )
        )

    def IsOk(self):
        """Checks if the rendering process is still alive

        Returns:
            bool: whether the simulation is still alive
        """
        return self.p.is_alive()

    def CheckForKeyPresses(self, check_for_key_presses):
        """Will tell the VehiclePlotter to check for keypresses

        Args:
            check_for_key_presses (bool): Whether the plotter should check if inputs
        """
        self.check_for_key_presses = check_for_key_presses
        self.q.put(self.check_for_key_presses)

    def GetKeyInput(self):
        """Will get the key input and reset it to None

        Returns:
            str: the key input
        """
        ret = self.key_input
        self.key_input = None
        return ret

    def __del__(self):
        """Destructor

        Will try to block and wait for the process to complete.
        """
        if hasattr(self, "p") and self.p.is_alive():
            self.p.join()


class WAMultipleVisualizations(WAVisualization):
    """Wrapper class for multiple visualizations. Allows multiple visualizations to be used.

    Args:
        visualizations (list): List of visualizations.
    """

    def __init__(self, visualizations):
        self.visualizations = visualizations

    def Synchronize(self, time, vehicle_inputs):
        """Synchronize each visualization at the specified time

        Args:
            time (double): the time at which the visualization should synchronize all modules
            vehicle_inputs (WAVehicleInputs): vehicle inputs
        """
        for vis in self.visualizations:
            vis.Synchronize(time, vehicle_inputs)

    def Advance(self, step):
        """Advance the state of each managed visualization

        Args:
            step (double): the time step at which the visualization should be advanced
        """
        for vis in self.visualizations:
            vis.Advance(step)