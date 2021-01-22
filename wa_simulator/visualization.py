"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

from abc import ABC, abstractmethod  # Abstract Base Class

# WA Simulator
from wa_simulator.inputs import WAVehicleInputs

# Other imports
from multiprocessing import Process, Pipe, Barrier, Queue, set_start_method
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import display, clear_output


class WAVisualization(ABC):
    """Base class to be used for visualization of the simulation world.

    Derived classes will use various world attributes to visualize the simulation
    """

    @abstractmethod
    def synchronize(self, time, vehicle_inputs):
        """Synchronize the visualization at the specified time with the passed vehicle inputs

        Args:
            time (double): time to synchronize the visualization to
            vehicle_inputs (WAVehicleInputs): inputs to the vehicle. Can be helpful for visualization (debug) purposes.
        """
        pass

    @abstractmethod
    def advance(self, step):
        """Advance the state of the visualization by the specified step

        Args:
            step (double): step size to update the visualization by
        """
        pass

    @abstractmethod
    def is_ok(self):
        """Verifies the visualization is running properly.

        Returns:
            bool: Whether the visualization is running correctly.
        """
        pass


class WAMultipleVisualizations(WAVisualization):
    """Wrapper class for multiple visualizations. Allows multiple visualizations to be used.

    Args:
        visualizations (list): List of visualizations.
    """

    def __init__(self, visualizations):
        self.visualizations = visualizations

    def synchronize(self, time, vehicle_inputs):
        """Synchronize each visualization at the specified time

        Args:
            time (double): the time at which the visualization should synchronize all modules
            vehicle_inputs (WAVehicleInputs): vehicle inputs
        """
        for vis in self.visualizations:
            vis.synchronize(time, vehicle_inputs)

    def advance(self, step):
        """Advance the state of each managed visualization

        Args:
            step (double): the time step at which the visualization should be advanced
        """
        for vis in self.visualizations:
            vis.advance(step)

    def is_ok(self):
        """Verifies the visualization is running properly.

        Returns:
            bool: Whether the visualization is running correctly.
        """
        for vis in self.visualizations:
            if not vis.is_ok():
                return False
        return True


class _MatplotlibVehicle:
    """Plotter class for a matplotlib vehicle"""

    def __init__(self, properties):
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

    def initialize(self, ax, cabcolor="-k", wheelcolor="-k"):
        """Initialize plotting for the matplotlib vehicle"""
        cab, = ax.plot(
            np.array(self.outline[0, :]).flatten(),
            np.array(self.outline[1, :]).flatten(),
            cabcolor,
        )
        fr, = ax.plot(
            np.array(self.fr_wheel[0, :]).flatten(),
            np.array(self.fr_wheel[1, :]).flatten(),
            wheelcolor,
        )
        rr, = ax.plot(
            np.array(self.rr_wheel[0, :]).flatten(),
            np.array(self.rr_wheel[1, :]).flatten(),
            wheelcolor,
        )
        fl, = ax.plot(
            np.array(self.fl_wheel[0, :]).flatten(),
            np.array(self.fl_wheel[1, :]).flatten(),
            wheelcolor,
        )
        rl, = ax.plot(
            np.array(self.rl_wheel[0, :]).flatten(),
            np.array(self.rl_wheel[1, :]).flatten(),
            wheelcolor,
        )
        self.mat_vehicle = (cab, fr, rr, fl, rl)

    def transform(self, entity, x, y, yaw, alpha=0, x_offset=0, y_offset=0):
        """Helper function to transfrom a numpy entity by the specified values"""
        T = np.array(
            [[np.cos(yaw), np.sin(yaw), x],
             [-np.sin(yaw), np.cos(yaw), y], [0, 0, 1]]
        )
        T = T @ np.array(
            [
                [np.cos(alpha), np.sin(alpha), x_offset],
                [-np.sin(alpha), np.cos(alpha), y_offset],
                [0, 0, 1],
            ]
        )
        return T.dot(entity)

    def update(self, x, y, yaw, steering):
        """Update the state of the matplotlib representation of the vehicle"""

        yaw *= -1
        steering *= -1

        # Update the position of each entity
        fr_wheel = self.transform(
            self.fr_wheel,
            x,
            y,
            yaw,
            alpha=steering,
            x_offset=self.Lf,
            y_offset=-self.track_width,
        )
        fl_wheel = self.transform(
            self.fl_wheel,
            x,
            y,
            yaw,
            alpha=steering,
            x_offset=self.Lf,
            y_offset=self.track_width,
        )
        rr_wheel = self.transform(
            self.rr_wheel, x, y, yaw, x_offset=-self.Lr, y_offset=-self.track_width
        )
        rl_wheel = self.transform(
            self.rl_wheel, x, y, yaw, x_offset=-self.Lr, y_offset=self.track_width
        )
        outline = self.transform(self.outline, x, y, yaw)

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


class _MatplotlibSimpleDashboard:
    """Simple dashboard with selected information that will be displayed within a matplotlib plot window"""

    def initialize(self, ax):
        """Initialize the annotation"""

        bbox_props = dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9)
        self.annotation = ax.annotate(
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

    def update(self, vehicle_inputs, time, speed):
        """Update the annotation"""
        text = (
            f"Time :: {time:.2f}\n"
            f"Steering :: {vehicle_inputs.steering:.2f}\n"
            f"Throttle :: {vehicle_inputs.throttle:.2f}\n"
            f"Braking :: {vehicle_inputs.braking:.2f}\n"
            f"Speed :: {speed:.2f}"
        )
        self.annotation.set_text(text)


class _MatplotlibPlotter(ABC):
    """Base class for matplotlib visualization"""

    class Event:
        def __init__(self, name, value):
            self.name = name
            self.value = value

    def __init__(self, mat_vehicle, dashboard, static=False, padding=25, xlim=(-50, 50), ylim=(50, -50)):
        self.mat_vehicle = mat_vehicle
        self.dashboard = dashboard

        self.vehicle_inputs = WAVehicleInputs()
        self.time = 0

        self.static = static
        self.padding = padding
        self.xlim = xlim
        self.ylim = ylim

        # Asynchronous Matplotlib events
        self.events = dict()

    def _initialize_plot(self):
        """Initialize a matplotlib plot and pass the axes to the vehicle and dashboard"""
        # Initial plotting setup
        self.fig, self.ax = plt.subplots(figsize=(8, 8))

        # Plot styling
        self.ax.set_xlim(*self.xlim)
        self.ax.set_ylim(*self.ylim)

        self.ax.grid(True)
        self.ax.set_aspect("equal", adjustable="box")

        # Initialize the plotters
        self.mat_vehicle.initialize(self.ax)
        self.dashboard.initialize(self.ax)

    def synchronize(self, time, vehicle_inputs):
        """Saves values to be visualized in matplotlib."""
        self.vehicle_inputs = vehicle_inputs
        self.time = time

    @abstractmethod
    def advance(self, step, state):
        pass

    @abstractmethod
    def register_key_press_event(self, callback):
        pass

    @abstractmethod
    def is_alive(self):
        pass

    @abstractmethod
    def plot(self, *args, **kwargs):
        pass

    def _update_axes(self, x, y):
        self.ax.set_xlim(x - self.padding, x + self.padding)
        self.ax.set_ylim(y + self.padding, y - self.padding)


class _MatplotlibSinglePlotter(_MatplotlibPlotter):
    """Single process plotter for sequential visualization. Can be used in jupyter"""

    def __init__(self, mat_vehicle, dashboard, is_jupyter=False, **kwargs):
        super().__init__(mat_vehicle, dashboard, **kwargs)

        self._initialize_plot()

        self.is_jupyter = is_jupyter

    def advance(self, step, state):
        # Extract values
        x, y, yaw, v = state

        # Update the simulation elements
        self.mat_vehicle.update(x, y, yaw, self.vehicle_inputs.steering)
        self.dashboard.update(self.vehicle_inputs, self.time, v)

        if not self.static:
            self._update_axes(x, y)

        # Update the plot
        if self.is_jupyter:
            display(self.fig)
            clear_output(wait=True)
        else:
            plt.pause(1e-9)

    def register_key_press_event(self, callback):
        self.fig.canvas.mpl_connect('key_press_event', self.key_press)
        self.events['key_press_event'] = callback

    def key_press(self, event):
        if event.name in self.events:
            self.events[event.name](event.key)

    def is_alive(self):
        return plt.fignum_exists(self.fig.number)

    def plot(self, *args, **kwargs):
        self.ax.plot(*args, **kwargs)


class _MatplotlibMultiPlotter(_MatplotlibPlotter):
    """Plotter used for situations where multiprocessing is desired. Faster than sequential."""

    class _SimulationState:
        def __init__(self, state, vehicle_inputs, time):
            self.state = state
            self.vehicle_inputs = vehicle_inputs
            self.time = time

        def __call__(self):
            return self.state, self.vehicle_inputs, self.time

    class _PlotCall:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    def __init__(self, mat_vehicle, dashboard, asynchronous=False, **kwargs):
        super().__init__(mat_vehicle, dashboard, **kwargs)

        self.asynchronous = asynchronous

        self.events['close_event'] = self.close

        # Initialize multiprocessing objects
        if plt.get_backend() == "MacOSX":
            set_start_method("spawn", force=True)

        # Communication pipelines between processes
        self.event_sender, self.event_receiver = Pipe()
        self.queue = Queue(1)

        # Barrier that will wait for initialization to occur
        self.barrier = Barrier(2)

        self.p = Process(target=self.run)
        self.p.start()

        # Wait for the matplotlib window to initialize
        self.barrier.wait()

    def advance(self, step, state):
        """Advance the state of the matplotlib window"""
        if self.event_receiver.poll():
            event = self.event_receiver.recv()
            if event.name in self.events:
                self.events[event.name](event.value)

        # Send the state to the other process to visualize
        state = self._SimulationState(state, self.vehicle_inputs, self.time)
        if not self.queue._closed:
            if self.asynchronous and self.queue.empty():
                self.queue.put_nowait(state)
            else:
                self.queue.put(state)

    def run(self):
        """Multiprocess starter method. Will initialize matplotlib and setup FuncAnimation"""
        # Initialize matplotlib
        self._initialize_plot()
        self.fig.canvas.mpl_connect('close_event', self.handle_close)

        # Initialize animation
        anim = FuncAnimation(self.fig, self.update, interval=10)

        # Synchronize with main process
        self.barrier.wait()

        plt.show()

        # Flush the queue
        if not self.queue.empty():
            self.queue.get_nowait()

    def update(self, i):
        """Called at a specific interval by FuncAnimation. Will update matplotlib window"""
        state = self.queue.get()
        if isinstance(state, self._SimulationState):
            (x, y, yaw, v), vehicle_inputs, time = state()

            self.mat_vehicle.update(x, y, yaw, vehicle_inputs.steering)
            self.dashboard.update(vehicle_inputs, time, v)

            if not self.static:
                self._update_axes(x, y)
        elif isinstance(state, str):
            if state == 'key_press_event':
                self.fig.canvas.mpl_connect('key_press_event', self.key_press)
        elif isinstance(state, self._PlotCall):
            self.ax.plot(*state.args, **state.kwargs)

    def handle_close(self, event):
        """Callback from matplotlib when a plot is closed"""
        self.event_sender.send(self.Event(event.name, ''))

    def register_key_press_event(self, callback):
        self.queue.put('key_press_event')
        self.events['key_press_event'] = callback

    def key_press(self, event):
        self.event_sender.send(self.Event(event.name, event.key))

    def is_alive(self):
        return self.p.is_alive()

    def plot(self, *args, **kwargs):
        self.queue.put(self._PlotCall(*args, **kwargs))

    def close(self, event):
        self.queue.close()
        self.event_receiver.close()
        self.event_sender.close()
        self.p.join()

    def __del__(self):
        """Destructor"""
        if hasattr(self, "p") and self.p.is_alive():
            self.p.join()


class WAMatplotlibVisualization(WAVisualization):
    """Matplotlib visualizer of the simulator world and the vehicle

    Args:
        vehicle (WAVehicle): vehicle to render in the matplotlib plot window
        system (WASystem): system used to grab certain parameters of the simulation
        plotter_type (str, optional): Type of plotter. "single" for single threaded, "multi" for multi threaded (fastest), "jupyter" if jupyter is used. Defaults to "single".

    Attributes:
        render_steps (int): steps between which the visualization should update
        vehicle (WAVehicle): vehicle to render in the matplotlib plot window
        system (WASystem): system used to grab certain parameters of the simulation
        mat_vehicle (_MatplotlibVehicle): a wrapper class used to create a visual representation of the vehicle in matplotlib
        dashboard (_MatplotlibSimpleDashboard): a wrapper class used to create a visual dashboard on the matplotlib window
        plotter (_MatplotlibPlotter): a wrapper class that handles matplotlib visualization and possible single/multi threading

    Raises:
        ValueError: plotter_type isn't recognized
    """

    def __init__(self, vehicle, system, plotter_type="single", **kwargs):
        self.render_steps = int(
            np.ceil(system.render_step_size / system.step_size))

        self.vehicle = vehicle
        self.system = system

        self.mat_vehicle = _MatplotlibVehicle(self.vehicle.vis_properties)
        self.dashboard = _MatplotlibSimpleDashboard()

        if plotter_type == "multi":
            self.plotter = _MatplotlibMultiPlotter(
                self.mat_vehicle, self.dashboard, **kwargs)
        elif plotter_type == "single" or plotter_type == "jupyter":
            self.plotter = _MatplotlibSinglePlotter(
                self.mat_vehicle, self.dashboard, is_jupyter=plotter_type == 'jupyter', **kwargs)
        else:
            raise ValueError(
                f"Unknown plotter type: {plotter_type}. Must be multi, single or jupyter")

    def synchronize(self, time, vehicle_inputs):
        """Synchronize the vehicle inputs to the values in this visualization

        Will just set class members

        Args:
            time (double): time at which to update the vehicle to
            vehicle_inputs (WAVehicleInputs): vehicle inputs
        """
        self.plotter.synchronize(time, vehicle_inputs)

    def advance(self, step):
        """Advance the state of the visualization by the specified step

        Will only call update if the scene should be rendered given the render step

        Args:
            step (double): step size to update the visualization by
        """
        if self.system.get_step_number() % self.render_steps == 0:
            self.plotter.advance(step, self.vehicle.get_simple_state())

    def is_ok(self):
        """Checks if the rendering process is still alive

        Returns:
            bool: whether the simulation is still alive
        """
        return self.plotter.is_alive()

    def register_key_press_event(self, callback):
        """Register a key press callback with the matplotlib visualization

        Args:
            callback (function): the callback to invoke when a key is pressed
        """
        self.plotter.register_key_press_event(callback)

    def plot(self, *args, **kwargs):
        """Pass plot info to the underyling plotter"""
        self.plotter.plot(*args, **kwargs)
