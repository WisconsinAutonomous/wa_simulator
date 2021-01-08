"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

from abc import ABC, abstractmethod  # Abstract Base Class

from ..utilities.data_loader import GetWADataFile  # WA Simulator


def LoadPropertiesFromJSON(filename, prop):
    """Load a specified property from a json specification file

    Will load a json file and extract the passed property field for use
    by the underyling vehicle object

    Args:
        filename (str): the filename location within the set WA data folder for the json file
        property (str): the property to get. Ex: "Vehicle Properties"

    Raises:
        ValueError: The property field isn't found

    Returns:
        dict: the property field extracted from the json file
    """
    import json

    full_filename = GetWADataFile(filename)

    with open(full_filename) as f:
        j = json.load(f)

    if prop not in j:
        raise ValueError(f"{prop} not found in json.")

    return j[prop]


class WAVehicle(ABC):
    """Base class for a WAVehicle.

    To implement a new vehicle model, override this class. A WAVehicle should interact
    with the terrain/assets/world and take three inputs: steering, throttle, braking.

    Args:
        filename (str, optional): Filename to be used for visualization properties

    Attributes:
        vis_properties (dict): Visual properties used for visualization of the vehicle.
    """

    def __init__(self, filename=None):
        self.vis_properties = (
            dict()
            if filename is None
            else LoadPropertiesFromJSON(filename, "Visualization Properties")
        )

    @abstractmethod
    def Synchronize(self, time, vehicle_inputs):
        """Synchronize the vehicle at the specified time and driver inputs

        Args:
            time (double): the time at which the synchronize the vehicle to
            vehicle_inputs (WAVehicleInputs): Inputs for the underyling dynamics
        """
        pass

    @abstractmethod
    def Advance(self, step):
        """Advance the vehicle by the specified step

        Args:
            step (double): how much to advance the vehicle by
        """
        pass

    @abstractmethod
    def GetSimpleState(self):
        """Get a simple state representation of the vehicle.

        Must return a tuple with the following values:
            (x position, y position, yaw about the Z, speed)
        """
        pass
