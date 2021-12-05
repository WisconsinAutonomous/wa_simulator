# WA Vehicle Simulator

The WA Simulator is a powerful, multi-platform, lightweight and *user-friendly* simulation platform for testing algorithms intended for autonomous robot or vehicle applications.
This project is under active development by [Wisconsin Autonomous](https://wa.wisc.edu/), a student organization at the University of Wisconsin - Madison.

## Usage

The WA Simulator is a lightweight tool meant to facilitate algorithm development. As a result, the majority of the actual vehicle dynamics is hidden behind the wa_simulator API. All you need to do is import the module and instantiate the classes.

### Default Usage

```python
# Import the wa_simulator
import wa_simulator as wa

def main():
    # Create the system
    system = wa.WASystem(step_size=1e-3)

    # Create an environment using a premade environment description
    env_filename = wa.WASimpleEnvironment.EGP_ENV_MODEL_FILE
    environment = wa.WASimpleEnvironment(system, env_filename)

    # Create an vehicle using a premade vehicle description
    vehicle_inputs = wa.WAVehicleInputs()
    veh_filename = wa.WALinearKinematicBicycle.GO_KART_MODEL_FILE
    vehicle = wa.WALinearKinematicBicycle(system, vehicle_inputs, veh_filename)

    # Visualize the simulation using matplotlib
    visualization = wa.WAMatplotlibVisualization(system, vehicle, vehicle_inputs, environment=environment)

    # Control the vehicle using the arrow keys
    controller = wa.WAMatplotlibController(system, vehicle_inputs, visualization)

    # Instantiate the simulation manager
    sim_manager = wa.WASimulationManager(system, environment, vehicle, visualizatioon, controller)

    # Simulation loop
    step_size = system.step_size
    while sim_manager.is_ok():
        time = system.time

        sim_manager.synchronize(time)
        sim_manager.advance(step_size)


if __name__ == "__main__":
    main()
```

### With Chrono

Using Chrono is as simple as changing a few file names and importing the chrono version of the simulator. Even though `wa_simulator.chrono` is the new import, all default `wa_simulator` classes are still accessible as seen above. [Background about Chrono can be found here](https://wisconsinautonomous.github.io/wa_simulator/background.html#ProjectChrono).

```python
# Import the wa_simulator
import wa_simulator.chrono as wa

def main():
    # Create the system
    system = wa.WAChronoSystem(step_size=1e-3)

    # Create an environment using a premade environment description
    env_filename = wa.WAChronoEnvironment.EGP_ENV_MODEL_FILE
    environment = wa.WAChronoEnvironment(system, env_filename)

    # Create an vehicle using a premade vehicle description
    vehicle_inputs = wa.WAVehicleInputs()
    veh_filename = wa.WAChronoVehicle.GO_KART_MODEL_FILE
    vehicle = wa.WAChronoVehicle(system, vehicle_inputs, environment, veh_filename)

    # Visualize the simulation using matplotlib
    visualization = wa.WAMatplotlibVisualization(system, vehicle, vehicle_inputs, environment=environment)

    # Control the vehicle using the arrow keys
    controller = wa.WAMatplotlibController(system, vehicle_inputs, visualization)

    # Instantiate the simulation manager
    sim_manager = wa.WASimulationManager(system, environment, vehicle, visualizatioon, controller)

    # Simulation loop
    step_size = system.step_size
    while sim_manager.is_ok():
        time = system.time

        sim_manager.synchronize(time)
        sim_manager.advance(step_size)


if __name__ == "__main__":
    main()
```

## Documentation

- [Home](https://wisconsinautonomous.github.io/wa_simulator/index.html)
- [Background](https://wisconsinautonomous.github.io/wa_simulator/background.html)
- [Installation](https://wisconsinautonomous.github.io/wa_simulator/install.html)
- [API Reference](https://wisconsinautonomous.github.io/wa_simulator/autoapi/wa_simulator/index.html)
- [PyPI](https://pypi.org/project/wa-simulator/)
- [Github](https://github.com/WisconsinAutonomous/wa_simulator)

## License 
`wa_simulator` is made available under the BSD-3 License. For more details, see [LICENSE](https://github.com/WisconsinAutonomous/wa_simulator/blob/develop/LICENSE).

## Support

Contact [Aaron Young](mailto:aryoung5@wisc.edu) for any questions or concerns regarding the contents of this repository.

## See Also

Stay up to date with our technical info by following our [blog](https://wa.wisc.edu/blog).

Follow us on [Facebook](https://www.facebook.com/wisconsinautonomous/), [Instagram](https://www.instagram.com/wisconsinautonomous/), and [LinkedIn](https://www.linkedin.com/company/wisconsin-autonomous/about/)!

<br>

<div>
	<img src="https://github.com/WisconsinAutonomous/wa-resources/blob/master/Images/WA.png?raw=true" alt="Wisconsin Autonomous Logo" class="readme-img" height="100px">  
	<img src="https://github.com/WisconsinAutonomous/wa-resources/blob/master/Images/UWCrest.png?raw=true" alt="University of Wisconsin - Madison Crest" class="readme-img" height="100px" align="right">
</div>
