# Change Log

## [2.1.0] - 2021-12-03

- Updated versioning to use `setuptools_scm` to automatically version

## [2.0.0] - 2021-12-03

Added `WABridge` to communicate with external entities

### Added

- `WABridge` which communicates with external entities
- Added `wasim` entry point to run `wa_simulator` in a Docker container automatically

## [Unreleased] - 2021-03-14

Made another push for additional API changes and additions

### Added

- WAEnvironment loader from json
- WATrack loader from json
- WAPath loader from json
- WAEnvironment, WATrack and WAPath json files

### Changed

- Made updates to API reference page
- Removed __add__, __sub__ and __mul__ from `WAQuaternion`
- Moved `inputs.py` to `vehicle_inputs.py`

## [Unreleased] - 2021-03-13

Made a large amount of API level changes and additions

### Added

- `WABase` has been added. It defines three methods: `synchronize`, `advance`, and `is_ok`. Simulation "components" should inherit from this class to implement their own functionality. Ex: vehicles, sensors or dynamic environments should inherit; static environments or path/track objects should not inherit from this class.

### Changed

- Most (almost all) closes do not have any attributes. Non-public methods and attributes are now hidden (prefixed with `_`) and are therefore not included in the documentation. For necessary items, getters and setters are now available.
- `WASimulation` is now `WASimulationManager`. The manager now takes in a `WASystem` and any number of `WABase` objects. These `WABase` objects are then updated throughout the simulation.
- Removed `WAPIDController` from the repo. Should be added to the demos. Reasoning being that it was not a great implementation and is not general enough for the repository.
- Removed `WATerrain`. Functionality now wrapped in `WAEnvironment`.
- Miscellaneous doc changes
- Continued adding new tests
- Adjusted data folder
