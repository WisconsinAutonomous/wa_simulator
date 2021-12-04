"""
Wisconsin Autonomous - https://wa.wisc.edu

Copyright (c) 2021 wa.wisc.edu
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

from abc import ABC, abstractmethod  # Abstract Base Class


class _WABaseMeta:
    def __new__(mcls, classname, bases, cls_dict):
        cls = super().__new__(mcls, classname, bases, cls_dict)
        for name, member in cls_dict.items():
            if not getattr(member, '__doc__'):
                member.__doc__ = getattr(bases[-1], name).__doc__
        return cls


class WABase(ABC):
    """The base Abstract Base Class for all WAComponents

    In the wa_simulator package, there are defined "components" that are *updatable*. An *updateable*
    component is most likely an entity that has dynamics and must manipulate or interact with the simulation.
    Some examples of *updateable* components: vehicles, sensors, environments/scenes, etc..

    All of these components should/must inherit from this base class. In that way, it forces the description
    of three methods: :meth:`~synchronize`, :meth:`~advance` and :meth:`~is_ok`. Furthermore, the
    :class:`~wa_simulator.simulation.WASimulationManager` class will expect components that inherit from
    :class:`WABase` (otherwise a :code:`TypeError` will be raised).

    .. highlight:: python
    .. code-block:: python

        # Example inhertiance
        # Many components that already inherit from WABase are provided
        # In most use cases for this simulator, simply inheriting from these 
        # classes will be sufficient/recommended

        from wa_simulator import WABase

        class WAVehicle(WABase):
            def synchronize(self, time):
                pass

            def advance(self, step):
                pass

            def is_ok(self):
                # Because this derives from WABase, the is_ok method can be initialized here 
                # and doesn't have to be implemented in any derived classes (i.e. WACar)
                pass

        class WACar(WAVehicle):
            def synchronize(self, time):
                pass

            def advance(self, step):
                pass

    As described above, this class only has two abstract methods: :meth:`~synchronize` and :meth:`~advance`. See their documentation
    for the motivation behind having two update style methods.
    """

    __metaclass__ = _WABaseMeta

    @abstractmethod
    def synchronize(self, time: float):
        """Update the state of this component at the current time.

        The primary reason to decouple the update method into two separate calls (i.e. :meth:`~synchronize` and :meth:`~advance`)
        is to provide flexibility to the user and is essentially semantic. In most simple cases, a user will only need one of the two. 
        Furthermore, can only use :meth:`~advance` if they prefer and just update their own :code:`time` variable. Given the unknown use cases
        for the simulator at the time of writing, it was chosen to provide two different methods with similar functionality as to allow
        the user to choose their desired implementation, rather than the writers of this package.

        As opposed to :meth:`~advance`, this method gets the current time of the simulation. As menthioned earlier, 
        :meth:`~advance` and a user defined `time` variable could be used to instead to hold the current state of the simulation. However,
        to aid in generality of the package, this method is provided to simply provide the current time of the simulation to the user in a decoupled
        manner from the :meth:`~advance` method.

        Args:
            time (float): The current time to synchronize to
        """
        pass

    @abstractmethod
    def advance(self, step: float):
        """Advance the state of this component by the specified time step.

        The primary reason to decouple the update method into two separate calls (i.e. :meth:`~synchronize` and :meth:`~advance`)
        is to provide flexibility to the user and is essentially semantic. In most simple cases, a user will only need one of the two. 
        Furthermore, can only use :meth:`~advance` if they prefer and just update their own :code:`time` variable. Given the unknown use cases
        for the simulator at the time of writing, it was chosen to provide two different methods with similar functionality as to allow
        the user to choose their desired implementation, rather than the writers of this package.

        Args:
            step (float): The step size to advance this component by
        """
        pass

    @abstractmethod
    def is_ok(self) -> bool:
        """Check whether this component is still alive.

        Depending the type of component, a specific element may "fail". For example, when
        a visualization is used that presents a GUI/window, if the user closes that display,
        this would be considered a component death. Therefore, :meth:`~is_ok` should then return
        False.

        Returns:
            bool: True if still alive, false otherwise
        """
        pass
