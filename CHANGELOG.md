# Change Log

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