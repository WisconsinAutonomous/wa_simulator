"""
Wisconsin Autonomous - https://wa.wisc.edu

Copyright (c) 2021 wa.wisc.edu
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

from abc import ABC, abstractmethod  # Abstract Base Class

# WA Simulator
from wa_simulator.base import WABase
from wa_simulator.core import WA_PI, WAVector
from wa_simulator.path import WAPath
from wa_simulator.track import WATrack
from wa_simulator.environment import WABody

# Other imports
from multiprocessing import Process, Pipe, Barrier, Queue, set_start_method
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Patch
import matplotlib.collections as collections
from matplotlib.animation import FuncAnimation
from IPython.display import display, clear_output


class WAVisualization(WABase):
    """Base class to be used for visualization of the simulation world.

    Inherits from WABase, so this class and any derived classes can be seen as components. Derived classes
    can/should use various world attributes to visualize the simulation. `Matplotlib <https://matplotlib.org/>`_ and
    `irrlicht <http://irrlicht.sourceforge.net/>`_ are two example visualizations that, depending on the simulation
    configuration, users may select. Additional visualizations may be implemented, as well.
    """

    @abstractmethod
    def synchronize(self, time: float):
        pass

    @abstractmethod
    def advance(self, step: float):
        pass

    @abstractmethod
    def is_ok(self) -> bool:
        pass

    @abstractmethod
    def visualize(self, assets, *args, **kwargs):
        """Helper method that visualizes some object(s) in the chosen visualizer

        Different visualizations will visualize the object(s) in different ways. This is an abstract method,
        so it must be implemented.

        Args:
            assets (list): The object(s) to visualize
            *args: Positional arguments that are specific to the underyling visualizer implementation
            **kwargs: Keyworded arguments that are specific to the underlying visualizer implementation
        """
        pass

# -------------------------
# Matplotlib helper classes
# -------------------------


def _transform(entity: np.ndarray, x: float, y: float, yaw: float, alpha: float = 0, x_offset: float = 0, y_offset: float = 0):
    """Helper function to transfrom a numpy entity by the specified values

    There are two transformations that occur. First is considered "static". A simple transformation matrix is constructed where
    the array is rotated by some yaw about the z and a translation from (0,0). A second transformation matrix is then dotted to
    "add" another transform that will account for the previous transformations. This second transformation is used for wheels which
    have the same rotation and position as the chassis, but also are offset and rotated by some value depending on the steering
    angle and the position of the tire relative to the COM.

    Args:
       entity (np.ndarray): The numpy array to transform
       x (float): The static x translation (offset will be applied post rotation)
       y (float): The static y translation (offset will be applied post rotation)
       yaw (float): The static rotation (alpha applied post this rotation)
       alpha (float): The steering angle rotation applied in the second matrix
       x_offset (float): The offset translation in the x direction applied in the second matrix
       y_offset (float): The offset translation in the y direction applied in the second matrix
    """
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


class _MatplotlibVehicle:
    """Plotter class for a matplotlib vehicle

    Required visualization properties (keys present in the :code:`properties` dictionary):
        "Tire Distance To Front" (float): Offset distance between the COM and the front axle
        "Tire Distance To Rear" (float): Offset distance between the COM and the rear axle
        "Body Distance To Front" (float): Offset distance between the COM and the front bumper
        "Body Distance To Rear" (float): Offset distance between the COM and the rear bumper
        "Body Width" (float): Width of the chassis
        "Tire Width" (float): Tread width of each tire
        "Tire Diameter" (float): Diameter of each tire (in a 2D visualization, will just be length)
        "Track Width" (float): Distance between the wheels on either side of the vehicle


    Args:
        properties (dict): The properties associated with the vehicle representation. See above for required keys.
    """

    def __init__(self, properties: dict):
        body_Lf = properties["Body Distance to Front"]
        body_Lr = properties["Body Distance to Rear"]
        body_width = properties["Body Width"]
        tire_width = properties["Tire Width"]
        tire_diameter = properties["Tire Diameter"]

        self._Lf = properties["Tire Distance to Front"]
        self._Lr = properties["Tire Distance to Rear"]
        self._track_width = properties["Track Width"]
        self._wheelbase = self._Lf + self._Lr

        # Visualization shapes
        self._outline = np.array(
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

        self._rr_wheel = np.copy(wheel)
        self._rl_wheel = np.copy(wheel)
        self._rl_wheel[1, :] *= -1

        self._fr_wheel = np.copy(wheel)
        self._fl_wheel = np.copy(wheel)
        self._fl_wheel[1, :] *= -1

    def initialize(self, ax, cabcolor: str = "-k", wheelcolor: str = "-k"):
        """Initialize the plotting window for the matplotlib vehicle

        Will save matplotlib returned objects to be used for plotting later.

        Args:
            ax (matplotlib.axes): the axes to plot the vehicle on
            cabcolor (str): The cab color in matplotlib readable format. Defaults to solid black.
            wheelcolor (str): The wheel color in matplotlib readable format. Defaults to solid black.
        """
        cab, = ax.plot(
            np.array(self._outline[0, :]).flatten(),
            np.array(self._outline[1, :]).flatten(),
            cabcolor,
        )
        fr, = ax.plot(
            np.array(self._fr_wheel[0, :]).flatten(),
            np.array(self._fr_wheel[1, :]).flatten(),
            wheelcolor,
        )
        rr, = ax.plot(
            np.array(self._rr_wheel[0, :]).flatten(),
            np.array(self._rr_wheel[1, :]).flatten(),
            wheelcolor,
        )
        fl, = ax.plot(
            np.array(self._fl_wheel[0, :]).flatten(),
            np.array(self._fl_wheel[1, :]).flatten(),
            wheelcolor,
        )
        rl, = ax.plot(
            np.array(self._rl_wheel[0, :]).flatten(),
            np.array(self._rl_wheel[1, :]).flatten(),
            wheelcolor,
        )

        # TODO: Do these variables go out of scope? Are variables copied?
        self._mat_vehicle = (cab, fr, rr, fl, rl)

    def update(self, x: float, y: float, yaw: float, steering: float):
        """Update the state of the matplotlib representation of the vehicle

        Args:
            x (float): x position of the vehicle
            y (float): y position of the vehicle
            yaw (float): yaw rotation of the vehicle about the z (up)
            steering (float): steering angle of the vehicle
        """

        # TODO: I think irrlicht is backwards, so flip plotting so steering and visuals match
        yaw *= -1
        steering *= -1

        # Update the position of each entity
        # All updates are copies of the original array, so each update is basically a fresh update
        fr_wheel = _transform(self._fr_wheel, x, y, yaw, alpha=steering, x_offset=self._Lf, y_offset=-self._track_width)
        fl_wheel = _transform(
            self._fl_wheel,
            x,
            y,
            yaw,
            alpha=steering,
            x_offset=self._Lf,
            y_offset=self._track_width,
        )
        rr_wheel = _transform(
            self._rr_wheel, x, y, yaw, x_offset=-self._Lr, y_offset=-self._track_width
        )
        rl_wheel = _transform(
            self._rl_wheel, x, y, yaw, x_offset=-self._Lr, y_offset=self._track_width
        )
        outline = _transform(self._outline, x, y, yaw)

        (cab, fr, rr, fl, rl) = self._mat_vehicle

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
    """Simple dashboard with selected information that will be displayed within a matplotlib plot window

    TODO: Can we make this a base class and have multiple dashboards (i.e. just make this configurable)
    """

    def initialize(self, ax):
        """Initialize the annotation

        Args:
            ax (matplotlib.axes): The axes to place the annotation on
        """

        bbox_props = dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9)
        self._annotation = ax.annotate(
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

    def update(self, vehicle_inputs: 'WAVehicleInputs', time: float, speed: float):
        """Update the dashboard

        Args:
            vehicle_inputs (WAVehicleInputs): The inputs for the vehicle. Visualized in the simple annotation.
            time (float): The current time of the simulation
            speed (float): The instantaneous speed of the vehicle
        """

        text = (
            f"Time :: {time:.2f}\n"
            f"Steering :: {vehicle_inputs.steering:.2f}\n"
            f"Throttle :: {vehicle_inputs.throttle:.2f}\n"
            f"Braking :: {vehicle_inputs.braking:.2f}\n"
            f"Speed :: {speed:.2f}"
        )
        self._annotation.set_text(text)


class _MatplotlibBody:
    """Simple body class for updateable assets

    Args:
        body (WABody): the body to visualize
    """

    def __init__(self, body):
        self._body = body

    def initialize(self, ax):
        """Initialize the body representation

        Args:
            ax (matplotlib.axes): The axes to place the annotation on
        """
        print(self._body.name)
        pass

    def update(self):
        """Update the body"""
        pass


class _MatplotlibBodyList:
    def __init__(self, bodies):
        self.bodies = bodies


class _MatplotlibPlotter(WABase):
    """Base class for matplotlib visualization

    Provides base implementation to be used for all subsequent implementors.

    Args:
        mat_vehicle (_MatplotlibVehicle): The matplotlib vehicle representation
        dashboard (_MatplotlibSimpleDashboard): The dashboard that displays information related to the vehicle state
        record (bool): If set to true, images will be saved under record_filename.
        record_folder (str): The folder to save images to.
        static (bool): if desireable, the matplotlib window can update its axes to "follow" the vehicle. Default is False (follows the vehicle)
        padding (float): Padding between the vehicle's COM and the border of the plot window. Default is 25
        xlim (tuple): x axis limits that are used if static is set to True
        ylim (tuple): y axis limits that are used if static is set to True
    """

    class _Event:
        """Event object that maintains the name of the event and the returned value.

        In matplotlib, callbacks have a name and typically a few class attributes available.
        In this simulator, we only need to pass around the values we want.

        Args:
            name (str): The name of the event
            value (any): The value associated with the event

        Attributes:
            name (str): The name of the event
            value (any): The value associated with the event
        """

        def __init__(self, name: str, value):
            self.name = name
            self.value = value

    def __init__(self, mat_vehicle: _MatplotlibVehicle, dashboard: _MatplotlibSimpleDashboard, opponent_mat_vehicles: list, record: bool, record_folder: str, static: bool = False, padding: float = 25, xlim: tuple = (-50, 50), ylim: tuple = (50, -50)):
        self._mat_vehicle = mat_vehicle
        self._dashboard = dashboard
        self._opponent_mat_vehicles = opponent_mat_vehicles

        self._record = record
        self._record_folder = record_folder

        if self._record:
            exit(0)

        self._save_number = 0

        self._vehicle_inputs = None
        self._state = (0, 0, 0, 0)
        self._time = 0

        self._static = static
        self._padding = padding
        self._xlim = xlim
        self._ylim = ylim

        # Asynchronous Matplotlib events
        self._events = dict()

    def set_vehicle(self, vehicle: 'WAVehicle'):
        """Set the vehicle object

        Args:
            vehicle (WAVehicle): The vehicle
        """
        self._vehicle = vehicle

    def set_vehicle_inputs(self, vehicle_inputs: 'WAVehicleInputs'):
        """Set the vehicle inputs object

        Args:
            vehicle_inputs (WAVehicleInputs): The vehicle inputs
        """
        self._vehicle_inputs = vehicle_inputs

    def set_opponents(self, opponents: list):
        """Set the opponents list

        Args:
            opponents (list): The list of opponents
        """
        self._opponents = opponents
        self._opponent_states = [[(0, 0, 0, 0), opponent._vehicle_inputs] for opponent in opponents]

    def synchronize(self, time: float):
        # Save values for later
        self._time = time

    def advance(self, step: float):
        # Update the state
        pos = self._vehicle.get_pos()
        yaw = self._vehicle.get_rot().to_euler_yaw()
        v = self._vehicle.get_pos_dt().length
        self._state = (pos.x, pos.y, yaw, v)

        for i, opponent in enumerate(self._opponents):
            pos = opponent.get_pos()
            yaw = opponent.get_rot().to_euler_yaw()
            v = opponent.get_pos_dt().length
            self._opponent_states[i][0] = (pos.x, pos.y, yaw, v)

    def _savefig(self):
        """Save a figure from matplotlib"""

        if self._record:
            if self._save_number == 0:
                import os
                if not os.path.exists(self._record_folder):
                    os.makedirs(self._record_folder)
                del os

            self._fig.savefig(self._record_folder + f'{self._save_number}.png', dpi=200)

            self._save_number += 1

    @abstractmethod
    def register_key_press_event(self, callback):
        """Register callback with a key press event in the matplotlib window

        # matplotlib.backend_bases.KeyEvent>`_ provide an event
        `Matplotlib KeyEvents <https://matplotlib.org/stable/api/backend_bases_api.html
        object with various attributes. In the case of controllers, we only really need the keypressed and not necessarily the location of anything.

        .. todo::
            Add support for more general callbacks (i.e. mouse)

        Args:
            callback (method(int)): A callable method that takes in an int (represents the key pressed)
        """
        pass

    @abstractmethod
    def plot(self, *args, **kwargs):
        """Plot additional information within the matplotlib window

        Args:
            *args: positional arguments that are passed to the underyling plotter (and subsequently to matplotlib)
            **kwargs: keyworded arguments that are passed to the underyling plotter (and subsequently to matplotlib)
        """
        pass

    def _initialize_plot(self):
        """Helper method that initializes a matplotlib plot and passes the axes to the vehicle and dashboard"""

        # Initial plotting setup
        self._fig, self._ax = plt.subplots(figsize=(8, 8))

        # Plot styling
        self._ax.set_xlim(*self._xlim)
        self._ax.set_ylim(*self._ylim)

        self._ax.grid(True)
        self._ax.set_aspect("equal", adjustable="box")

        # Initialize the plotters
        self._mat_vehicle.initialize(self._ax)
        self._dashboard.initialize(self._ax)
        for o in self._opponent_mat_vehicles:
            o.initialize(self._ax)

    def _update_axes(self, x, y):
        """Helper method to update the matplotlib axis plot.

        Moving vehicles commonly want to be "followed". This method will place the vehicle at the center of the window and adjust
        the axes accordingly. The padding specified at initialization will be added.

        Args:
            x (float): x position of the vehicle
            y (float): y position of the vehicle
        """
        self._ax.set_xlim(x - self._padding, x + self._padding)
        self._ax.set_ylim(y + self._padding, y - self._padding)


class _MatplotlibSinglePlotter(_MatplotlibPlotter):
    """Single process plotter for sequential visualization. Can be used in jupyter.

    A single threaded plotter basically will update it's state `in order` with other components. This can be thought of
    as the typical use case for matplotlib where :code:`plt.show()`/:code:`plt.pause()` comes directly after `plt.plot`.

    For jupyter, we need to use IPython to basically create an image and display that image in the jupyter browser. This really sucks
    cause it's super slow. TODO: Is there a faster way to do that?

    Args:
        mat_vehicle (_MatplotlibVehicle): The matplotlib vehicle representation
        dashboard (_MatplotlibSimpleDashboard): The dashboard that displays information related to the vehicle state
        is_jupyter (bool): should jupyter visualization be used (i.e. IPython display)?
        record (bool, optional): If set to true, images will be saved under record_filename. Defaults to False (doesn't save images).
        record_folder (str, optional): The folder to save images to. Defaults to "OUTPUT/".
        **kwargs: keyworded arguments used for the base _MatplotlibPlotter class
    """

    def __init__(self, mat_vehicle, dashboard, opponent_mat_vehicles, is_jupyter: bool = False, record: bool = False, record_folder: str = "OUTPUT/", **kwargs):
        super().__init__(mat_vehicle, dashboard, opponent_mat_vehicles, record, record_folder, **kwargs)

        self._initialize_plot()

        self._is_jupyter = is_jupyter

    def advance(self, step):
        super().advance(step)

        # Extract values
        x, y, yaw, v = self._state

        # Update the simulation elements
        self._mat_vehicle.update(x, y, yaw, self._vehicle_inputs.steering)
        self._dashboard.update(self._vehicle_inputs, self._time, v)

        # Update the axes to "follow" the vehicle
        if not self._static:
            self._update_axes(x, y)

        for i, (state, vehicle_inputs) in enumerate(self._opponent_states):
            x, y, yaw, v = state
            self._opponent_mat_vehicles[i].update(x, y, yaw, vehicle_inputs.steering)

        # Update the plot
        if self._is_jupyter:
            display(self._fig)
            clear_output(wait=True)
        else:
            plt.pause(1e-9)

        # Save (if desired)
        self._savefig()

    def is_ok(self):
        return plt.fignum_exists(self._fig.number)

    def register_key_press_event(self, callback):
        self._fig.canvas.mpl_connect('key_press_event', self._key_press)
        self._events['key_press_event'] = callback

    def plot(self, *args, **kwargs):
        if isinstance(args[0], Patch):
            self._ax.add_patch(args[0])
        elif isinstance(args[0], collections.Collection):
            self._ax.add_collection(args[0])
        else:
            self._ax.plot(*args, **kwargs)

    def _key_press(self, event):
        """Key press callback. Passes the event key (i.e. 'up' or 'a') to the callback registered through :meth:`~register_key_press_event`.

        Args:
            event (matplotlib.event): event with a name and key attribute
        """
        if event.name in self._events:
            # Call that event with the event key (is a string like 'up' or 'a')
            self._events[event.name](event.key)


class _MatplotlibMultiPlotter(_MatplotlibPlotter):
    """Multi process plotter for sequential visualization. Significantly faster than the sequential :class:`~_MatplotlibSinglePlotter`.

    A multi threaded plotter will basically update it's state at a fixed rate. All visualizations occur in a separate thread, so
    a synchronized queue is used to pass information between threads. At the fixed rate, on an update, that information is grabbed from the front
    of the queue. Stale information is always ignored so there is only ever 1 or 0 packets in the queue. A `asynchronous` constructor parameter
    provides the configurability to either wait for state information to be used or continue and just throw out old state data. The
    latter results in the simulation progressing significantly faster than the plotter, so it's not recommended.

    Two communication methods are used. One is a queue and is used strictly for state information and the other is a Pipe and used for simulation
    communication related items, such as keyboard callback registration.

    Args:
        mat_vehicle (_MatplotlibVehicle): The matplotlib vehicle representation
        dashboard (_MatplotlibSimpleDashboard): The dashboard that displays information related to the vehicle state
        asynchronous (bool, optional): If true, the plotter will continue without waiting for the passed state information to be used. Defaults to synchronous.
        record (bool, optional): If set to true, images will be saved under record_filename. Defaults to False (doesn't save images).
        record_folder (str, optional): The folder to save images to. Defaults to "OUTPUT/".
        **kwargs: keyworded arguments used for the base _MatplotlibPlotter class
    """

    class _SimulationState:
        """Simulation state helper class that just holds various attributes for plotting

        Pickable to pass between threads.

        Args:
            state (tuple): holds (x,y,yaw,steering)
            vehicle_inputs (WAVehicleInputs): the inputs to the vehicle
            time (float): the current time of the simulation

        Attributes:
            state (tuple): holds (x,y,yaw,steering)
            vehicle_inputs (WAVehicleInputs): the inputs to the vehicle
            time (float): the current time of the simulation
        """

        def __init__(self, state: tuple, vehicle_inputs: 'WAVehicleInputs', time: float):
            self.state = state
            self.vehicle_inputs = vehicle_inputs
            self.time = time

        def __call__(self):
            return self.state, self.vehicle_inputs, self.time

    class _PlotCall:
        """Pickable plot call that is passed to the plotter thread.

        Args:
            *args: Positional arguments used in matplotlib.plot
            **kwargs: Keyworded arguments used in matplotlib.plot

        Attributes:
            args: Positional arguments used in matplotlib.plot
            kwargs: Keyworded arguments used in matplotlib.plot
        """

        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    def __init__(self, mat_vehicle: '_MatplotlibVehicle', dashboard: '_MatplotlibSimpleDashboard', opponent_mat_vehicles: list, asynchronous: bool = False, record: bool = False, record_folder: str = "OUTPUT/", **kwargs):
        super().__init__(mat_vehicle, dashboard, opponent_mat_vehicles, record, record_folder, **kwargs)

        self._asynchronous = asynchronous

        self._events['close_event'] = self._close

        # Initialize multiprocessing objects
        if plt.get_backend() == "MacOSX":
            set_start_method("spawn", force=True)

        # Communication pipelines between processes
        self._event_sender, self._event_receiver = Pipe()
        self._queue = Queue(1)

        # Barrier that will wait for initialization to occur
        self._barrier = Barrier(2)

        self._p = Process(target=self.run)
        self._p.start()

        # Wait for the matplotlib window to initialize
        self._barrier.wait()

    def advance(self, step):
        super().advance(step)

        if self._event_receiver.poll():
            event = self._event_receiver.recv()
            if event.name in self._events:
                self._events[event.name](event.value)

        # Send the state to the other process to visualize
        def send(state):
            if not self._queue._closed:
                if self._asynchronous and self._queue.empty():
                    self._queue.put_nowait(state)
                else:
                    self._queue.put(state)

        states = [self._SimulationState(self._state, self._vehicle_inputs, self._time)]
        for state, vehicle_inputs in self._opponent_states:
            states.append(self._SimulationState(state, vehicle_inputs, self._time))
        send(states)

    def run(self):
        """Multiprocess starter method. Will initialize matplotlib and setup FuncAnimation"""

        # Initialize matplotlib
        self._initialize_plot()
        self._fig.canvas.mpl_connect('close_event', self._handle_close)

        # Initialize animation
        anim = FuncAnimation(self._fig, self._update, interval=10)

        # Synchronize with main process
        self._barrier.wait()

        plt.show()

        # Flush the queue
        if not self._queue.empty():
            self._queue.get_nowait()

    def _update(self, i: int):
        """Called at a specific interval by FuncAnimation. Will update matplotlib window

        Args:
            i (int): window count
        """
        try:
            state = self._queue.get(timeout=10 if i <= 2 else 1)
        except:
            plt.close(self._fig)
            return

        if isinstance(state, self._SimulationState):
            (x, y, yaw, v), vehicle_inputs, time = state()

            self._mat_vehicle.update(x, y, yaw, vehicle_inputs.steering)
            self._dashboard.update(vehicle_inputs, time, v)

            if not self._static:
                self._update_axes(x, y)
        elif isinstance(state, list):
            this_state = state[0]
            (x, y, yaw, v), vehicle_inputs, time = this_state()

            self._mat_vehicle.update(x, y, yaw, vehicle_inputs.steering)
            self._dashboard.update(vehicle_inputs, time, v)

            if not self._static:
                self._update_axes(x, y)

            for i, opponent in enumerate(state[1:]):
                (x, y, yaw, v), vehicle_inputs, time = opponent()

                self._opponent_mat_vehicles[i].update(x, y, yaw, vehicle_inputs.steering)

            # Save (if desired)
            self._savefig()

        elif isinstance(state, str):
            if state == 'key_press_event':
                self._fig.canvas.mpl_connect('key_press_event', self._key_press)
        elif isinstance(state, self._PlotCall):
            if isinstance(state.args[0], Patch):
                self._ax.add_patch(state.args[0])
            elif isinstance(state.args[0], collections.Collection):
                self._ax.add_collection(state.args[0])
            elif isinstance(state.args[0], _MatplotlibBodyList):
                for body in state.args[0].bodies:
                    body.initialize(self._ax)
            else:

                self._ax.plot(*state.args, **state.kwargs)

    def is_ok(self) -> bool:
        return self._p.is_alive()

    def plot(self, *args, **kwargs):
        self._queue.put(self._PlotCall(*args, **kwargs))

    def register_key_press_event(self, callback):
        self._queue.put('key_press_event')
        self._events['key_press_event'] = callback

    def _handle_close(self, event):
        """Callback from matplotlib when a plot is closed"""
        self._event_sender.send(self._Event(event.name, 'close_event'))

    def _key_press(self, event):
        """Key press callback. Passes the event key (i.e. 'up' or 'a') to the callback registered through :meth:`~register_key_press_event`.

        Args:
            event (matplotlib.event): event with a name and key attribute
        """
        self._event_sender.send(self._Event(event.name, event.key))

    def _close(self, event):
        """Close callback"""
        self._queue.close()
        self._event_receiver.close()
        self._event_sender.close()
        self._p.join()

    def __del__(self):
        """Destructor"""
        if hasattr(self, "p") and self._p.is_alive():
            self._p.join()


class WAMatplotlibVisualization(WAVisualization):
    """Matplotlib visualizer of the simulator world and the vehicle

    Plotter requires a vehicle and should be used for vehicle simulations where a 2d world representation is adequate. Furthermore,
    for vehicle models that aren't implemented through Chrono, this is the only implemented visualization for users.

    There are three types of matplotlib plotters currently implemented: "single", "multi" and "jupyter". Each has a different purpose with the same
    goal (to visualize the simulation).

    * single:

      * Uses a single thread where visualization updates are done sequentially with other simulation components.

      * *Worse performance than multi*.

    * multi:

      * Uses two threads where visualization updates are placed on a separate threads and updates are asynchronous. State information of the environment and vehicle are passed to the plotter on each update, but updates of the visuals are done at a fixed rate(10 [Hz]).

      * *Better performance than single*.

    * jupyter:

      * Supports visualization of a matplotlib window in a `jupyter notebook <https://jupyter.org/>`_.

      * *Performance is very poor*. *Do not use outside of jupyter*.

    Args:
        system (WASystem): system used to grab certain parameters of the simulation
        vehicle (WAVehicle): vehicle to render in the matplotlib plot window
        vehicle_inputs (WAVehicleInputs): the vehicle inputs
        environment (WAEnvironment, optional): An environment with various world assets to visualize. Defaults to None (doesn't visualize anything).
        plotter_type (str, optional): Type of plotter. "single" for single threaded, "multi" for multi threaded (fastest), "jupyter" if jupyter is used. Defaults to "single".
        opponents (list, optional): List of other :class:`~WAVehicle`'s that represent opponents. Used for rendering.
        record (bool, optional): If set to true, images will be saved under record_filename. Defaults to False (doesn't save images).
        record_folder (str, optional): The folder to save images to. Defaults to "OUTPUT/".
        **kwargs: Additional arguments that are based to the underlying plotter implementation.

    Raises:
        ValueError: plotter_type isn't recognized
    """

    def __init__(self, system: 'WASystem', vehicle: 'WAVehicle', vehicle_inputs: 'WAVehicleInputs', environment: 'WAEnvironment' = None,  plotter_type: str = "single", opponents: list = [], record: bool = False, record_folder: str = "OUTPUT/", **kwargs):
        self._system = system
        self._vehicle = vehicle
        self._vehicle_inputs = vehicle_inputs

        self._render_steps = int(np.ceil(system.render_step_size / system.step_size))  # noqa

        # Create the vehicle and dashboard
        mat_vehicle = _MatplotlibVehicle(self._vehicle.get_visual_properties())
        dashboard = _MatplotlibSimpleDashboard()

        opponent_mat_vehicles = []
        for opponent in opponents:
            opponent_mat_vehicles.append(_MatplotlibVehicle(opponent.get_visual_properties()))

        supported_plotters = ['multi', 'single', 'jupyter']

        # Create the underlying plotter
        if plotter_type == "multi":
            self._plotter = _MatplotlibMultiPlotter(
                mat_vehicle, dashboard, opponent_mat_vehicles, record=record, record_folder=record_folder, **kwargs)
        elif plotter_type == "single" or plotter_type == "jupyter":
            is_jupyter = plotter_type == 'jupyter'
            self._plotter = _MatplotlibSinglePlotter(
                mat_vehicle, dashboard, opponent_mat_vehicles, is_jupyter=is_jupyter, record=record, record_folder=record_folder, **kwargs)
        else:
            raise ValueError(
                f"Unknown plotter type: {plotter_type}. Must be one of the following: {', '.join(supported_plotters)}")

        self._plotter.set_vehicle(vehicle)
        self._plotter.set_vehicle_inputs(vehicle_inputs)
        self._plotter.set_opponents(opponents)

        if environment is not None:
            self.visualize(environment.get_assets())

    def synchronize(self, time: float):
        self._plotter.synchronize(time)

    def advance(self, step: float):
        if self._system.step_number % self._render_steps == 0:
            # Will only call advance at the rate specified by render_step_size in the passed system
            self._plotter.advance(step)

    def is_ok(self) -> bool:
        return self._plotter.is_ok()

    def register_key_press_event(self, callback):
        """Register a key press callback with the matplotlib visualization

        Args:
            callback(function): the callback to invoke when a key is pressed
        """
        self._plotter.register_key_press_event(callback)

    def plot(self, *args, **kwargs):
        """Pass plot info to the underyling plotter

        In some cases, additional information will want to be plotted in the plotter window. For example, in a vehicle simulation where
        a controller is attempting to follow a path, that path may want to be visualized in the matplotlib window. This method faciliates
        that functionality.

        See the `matplotlib docs <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html>`_ to see additional *args and **kwargs arguments.

        Args:
            *args: positional arguments that are passed to the underyling plotter (and subsequently to matplotlib)
            **kwargs: keyworded arguments that are passed to the underyling plotter (and subsequently to matplotlib)
        """
        self._plotter.plot(*args, **kwargs)

    def visualize(self, assets, *args, **kwargs):
        if not isinstance(assets, list):
            assets = [assets]

        patches = []
        bodies = []

        for i, asset in enumerate(assets):
            if isinstance(asset, WAPath):
                points = asset.get_points()
                self._plotter.plot(points[:, 0], points[:, 1], *args, **asset.get_vis_properties(), **kwargs)
            elif isinstance(asset, WATrack):
                self.visualize(asset.left, *args, **kwargs)
                self.visualize(asset.right, *args, **kwargs)
                self.visualize(asset.center, *args, **kwargs)
            elif isinstance(asset, WABody):
                if not hasattr(asset, 'size') or not hasattr(asset, 'position'):
                    raise AttributeError("Body must have 'size', and 'position' fields")

                if hasattr(asset, 'updates') and asset.updates:
                    # bodies.append(_MatplotlibBody(asset))
                    print(
                        "WARNING: updateable WABody's are currently not supported for the WAMatplotlibVisualization. This will come in a future release.")
                    continue

                position = asset.position
                yaw = 0 if not hasattr(asset, 'yaw') else asset.yaw
                size = asset.size / 2
                color = WAVector([1, 0, 0]) if not hasattr(asset, 'color') else asset.color

                # Can't really see white
                edgecolor = color
                if color == WAVector([1, 1, 1]):
                    edgecolor = WAVector([0, 0, 0])

                outline = np.array([[-size.y, size.y, size.y, -size.y, -size.y],
                                    [size.x, size.x, -size.x, -size.x, size.x],
                                    [1, 1, 1, 1, 1]])

                outline = _transform(outline, position.x, position.y, yaw)

                patches.append(Polygon(outline[:2, :].T, facecolor=color, edgecolor=edgecolor, alpha=0.4))

        if len(patches):
            self._plotter.plot(collections.PatchCollection(patches, match_original=True))
        if len(bodies):
            self._plotter.plot(_MatplotlibBodyList(bodies))
