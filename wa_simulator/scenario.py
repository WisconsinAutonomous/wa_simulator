"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# WA Simulator
from wa_simulator.base import WABase
from wa_simulator.utils import _load_json, _check_field, get_wa_data_file


class WAScenarioManager(WABase):
    """A manager for creating simulator scenarios from json files.

    The scenario manager will take in a json file that describes a "scenario".
    The idea behind scenarios is that it streamlines the ability for users to
    create complex environments with objects, vehicles and other entities simply
    through json (and without much code). Further, these scenarios may be dynamic;
    vehicles or objects may move, and these files support scenarios like this.
    """

    def __init__(self, system: 'WASystem', filename: str):
        self._system = system
        self._filename = filename

        # Read the json file
        # We'll start to load the objects specified in the file here
        j = _load_json(filename)

        # Validate the json file
        _check_field(j, "Type", value="Scenario")
        _check_field(j, "Template", value="WAScenarioManager")
        _check_field(j, "Environment", field_type=dict, optional=True)
        _check_field(j, "Vehicle", field_type=dict, optional=True)
        _check_field(j, "Visualization", field_type=dict, optional=True)

        # Create a map for all the class mappings
        # Makes it so we can instantiate the class simply from the module + name string
        def all_subclasses(cls):
            return set(cls.__subclasses__()).union(
                [s for c in cls.__subclasses__() for s in all_subclasses(c)])

        self._obj_map = {
            f"{c.__module__}.{c.__name__}": c for c in all_subclasses(WABase)}

        # Look for defined objects we know of
        if "Environment" in j:
            self.create_environment(j["Environment"])
        if "Vehicle" in j:
            self.create_vehicle(j["Vehicle"])
        if "Visualization" in j:
            self.create_visualization(j["Visualization"])

    def create_environment(self, j):
        pass

    def create_vehicle(self, j):
        from wa_simulator.vehicle_inputs import WAVehicleInputs

        # Validate the json file
        _check_field(j, "Type", field_type=str)
        _check_field(j, "Input File", field_type=str)
        _check_field(j, "Position", field_type=list, optional=True)

        # Load the vehicle through json
        veh_type = j["Type"]
        obj = self._obj_map[veh_type]

        veh_filename = j["Input File"]
        if hasattr(obj, veh_filename):
            veh_filename = getattr(obj, veh_filename)

        vehicle_inputs = WAVehicleInputs()
        vehicle = obj(self._system, vehicle_inputs, veh_filename)

    def create_visualization(self, j):
        pass

    def synchronize(self, time: float):
        pass

    def advance(self, step: float):
        pass

    def is_ok(self) -> bool:
        return True
