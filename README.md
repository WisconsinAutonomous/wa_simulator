# WA Vehicle Simulator


The WA Simulator is a powerful, multi-platform, lightweight and *user-friendly* simulation platform for testing algorithms intended for autonomous robot or vehicle applications.
This project is under active development by [Wisconsin Autonomous](https://wisconsinautonomous.org/), a student organization at the University of Wisconsin - Madison.

## Usage

The WA Simulator is a lightweight tool meant to facilitate algorithm development. As a result, the majority of the actual vehicle dynamics is hidden behind the wa_simulator API. All you need to do is import the module and instantiate the classes.

#### Default Usage

```python
# Import the wa_simulator
import wa_simulator as wa

def main():
    # Create the system
    sys = wa.WASystem(step_size=1e-3)

    # Create an environment using a premade environment description
    env_filename = wa.WASimpleEnvironment.EGP_ENV_MODEL_FILE
    env = wa.WASimpleEnvironment(env_filename, sys)

    # Create an vehicle using a premade vehicle description
    veh_filename = wa.WALinearKinematicBicycle.GO_KART_MODEL_FILE
    veh = wa.WALinearKinematicBicycle(veh_filename)

    # Visualize the simulation using matplotlib
    vis = wa.WAMatplotlibVisualization(veh, sys)

    # Control the vehicle using the arrow keys
    ctr = wa.WAMatplotlibController(sys, vis)

    # Instantiate the simulation manager
    sim = wa.WASimulation(sys, env, veh, vis, ctr)

    # Run the simulation
    sim.Run()


if __name__ == "__main__":
    main()
```

#### With Chrono

Using Chrono is as simple as changing a few file names and importing the chrono version of the simulator. Even though `wa_simulator.chrono` is the new import, all default `wa_simulator` classes are still accessible as seen above. [Background about Chrono can be found here](https://wisconsinautonomous.github.io/wa_simulator/background.html#ProjectChrono).

```python
# Import the wa_simulator
import wa_simulator.chrono as wa

def main():
    # Create the system
    sys = wa.WAChronoSystem(step_size=1e-3)

    # Create an environment using a premade environment description
    env_filename = wa.WAChronoEnvironment.EGP_ENV_MODEL_FILE
    env = wa.WAChronoEnvironment(env_filename, sys)

    # Create an vehicle using a premade vehicle description
    veh_filename = wa.WAChronoVehicle.GO_KART_MODEL_FILE
    veh = wa.WAChronoVehicle(veh_filename)

    # Visualize the simulation using matplotlib
    vis = wa.WAMatplotlibVisualization(veh, sys)

    # Control the vehicle using the arrow keys
    ctr = wa.WAMatplotlibController(sys, vis)

    # Instantiate the simulation manager
    sim = wa.WASimulation(sys, env, veh, vis, ctr)

    # Run the simulation
    sim.Run()


if __name__ == "__main__":
    main()
```

## Setup Guide

Detailed installation guides for this repository have been written for Windows and Unix based operating systems (separate MacOS and Linux guides are available). Please follow the guide that is relevant to the operating system you're using.

<!-- Windows: [Setup Guide](https://github.com/WisconsinAutonomous/control_sandbox/blob/master/WindowsSetup.md)\ -->
<!-- Mac: [Setup Guide](https://github.com/WisconsinAutonomous/control_sandbox/blob/master/UnixSetup.md) -->
<!-- Linux: [Setup Guide](https://github.com/WisconsinAutonomous/control_sandbox/blob/master/UnixSetup.md) -->

## License 
wa_simulator is made available under the BSD-3 License. For more details, see [LICENSE](https://github.com/WisconsinAutonomous/wa_simulator/blob/develop/LICENSE).


## Support

Contact [Aaron Young](aryoung5@wisc.edu) for any questions or concerns regarding the contents of this repository.

## See Also

Stay up to date with our technical info by following our [blog](https://www.wisconsinautonomous.org/blog).

Follow us on [Facebook](https://www.facebook.com/wisconsinautonomous/), [Instagram](https://www.instagram.com/wisconsinautonomous/), and [LinkedIn](https://www.linkedin.com/company/wisconsin-autonomous/about/)!

<br>

<div>
	<img src="https://github.com/WisconsinAutonomous/wa-resources/blob/master/Images/WA.png?raw=true" alt="Wisconsin Autonomous Logo" class="readme-img" height="100px">  
	<img src="https://github.com/WisconsinAutonomous/wa-resources/blob/master/Images/UWCrest.png?raw=true" alt="University of Wisconsin - Madison Crest" class="readme-img" height="100px" align="right">
</div>