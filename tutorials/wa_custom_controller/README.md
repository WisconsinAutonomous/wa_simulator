# Creating a Custom Controller

In this tutorial, we will create a custom controller that reads in commands via a `.csv` file.

## Prerequisites

- Basic understanding of the command line
- Basic understanding of Python
- You have `wa_simulator` installed ([resources for that](https://wisconsinautonomous.github.io/wa_simulator/installation/index.html))

> Note #1: This tutorial assumes you have installed the wa_simulator via Anaconda

> Note #2: This tutorial is meant for people using a Linux distribution or MacOS. It should work for Windows users within the Anaconda shell, but it hasn't been tested.
## Setup

Since `wa_simulator` is installed via `conda`, creating a custom demo and controller is as easy as creating a single file. That is what we'll do in this tutorial.

Please `cd` into a location where you would like to place these files. Create a directory called `wa_custom_controller` with two files: `custom_controller_demo.py` and `controller_data.csv`. Your file structure should look like this:
```
wa_custom_controller
├── custom_controller_demo.py
└── controller_data.csv
```

## Create the Controller

To begin, open `custom_controller_demo.py` in your favorite editor. I recommend [Atom](https://atom.io/) or [Visual Studio Code](https://code.visualstudio.com/).

All controllers in the `wa_simulator` must [inherit](https://www.w3schools.com/python/python_inheritance.asp) from the `WAController` class. Our custom class is no exception. [Per the documentation](https://wisconsinautonomous.github.io/wa_simulator/autoapi/wa_simulator/controller/index.html#wa_simulator.controller.WAController), our class _must_ implement the `synchronize`, `advance` abd `is_ok` methods. The `WAController's` constructor takes a `WASystem` and a shared `WAVehicleInputs` object, so we need to have those to pass it to the underlying controller. We will also need to have a csv file that we'll read, so let's pass that in the constructor. Let's create our class and implement these methods.

```python
import wa_simulator as wa

class CustomCSVController(wa.WAController):
    """Simple controller that controls the car from data in a csv file"""

    def __init__(self, sys, veh_inputs, csv_file):
        pass

    def synchronize(self, time):
        pass

    def advance(self, step):
        pass

    def is_ok(self):
        # Will just always return true
        return True
```

With the skeleton done, let's start implementing our classes. In the `__init__` function, we need to do a bit of house keeping. First, let's save the passed csv_file so we can edit it later. Also, we want to make sure the csv file is structured how we expect before reading it, so let's call a function to verify everything's correct and then read the file. The `__init__` function should now look like this:

```python
...

    def __init__(self, sys, veh_inputs, csv_file):
        super().__init__(sys, veh_inputs) # Calls the WAController's constructor

        self.csv_file = csv_file

        # to be implemented next
        self.ctlr_data = self.read_file(self.csv_file) 
...
```

Since we've now introduced the `read_file` method, we'll think a little bit about how we want the csv file to actually be structured.

### CSV Structure

A comma-separated values (csv) file is a intuitive way for structuring easily manipulated data. A typical csv may look like the following:
```
x,y,z # Header
0,0,0 # Entries ↓
1,1,1
2,2,2
.,.,.
.,.,.
```

The header line describes what each column represents and each entry is the actual data. We will structure our data in the following format: `time,steering,throttle,braking`. Basically, at `time`, the `steering`, `throttle`, and `braking` values will be passed to the vehicle. As an example, feel free to use the following file or create your own. Place the information in the `controller_data.csv` we created earlier.

```
time,steering,throttle,braking
0,0,0.1,0
1,1,0.1,0
5,-1,0.1,0
7.5,-1,1,0
10,0,0,1
```

As you can see in the file, we should expect to see the vehicle accelerate slowly for 1 second, begin to turn right, then turn left, accelerate even more and then brake at 10 seconds.

### Parse the CSV
Now we need to actually parse the data we created. As mentioned earlier, let's implement a method to check that the data is in the right format and then let's actually read in the data and place it in a variable called `ctlr_data`.

To make things easier, we'll us `NumPy's` `genfromtxt` method to do the heavylifting. As a result, make sure you place `import numpy as np` at the top of the `custom_controller_demo.py` file. 
```python
import numpy as np

...

    def read_file(self, file):
        # a delimiter is the thing that separates each data value in a row
        # data is now a numpy array with our data
        data = np.genfromtxt(file, delimiter=',', names=True)

        # Errors may occur with the above method, like if delimiter is wrong or inconsistent names

        # Check to make sure the data is as we expected
        if data.dtype.names != ('time', 'steering', 'throttle', 'braking') or np.isnan([r.tolist() for r in data]).any():
            raise ValueError('The csv file is not structured incorrectly!')

        return data
...

```

### Implement the Advance and Synchronize Methods
With the data parsed, we can now implement our controller logic. We basically want to check at every `Synchronize` call whether the time is equal to or past some point in our data. We will then pass the vehicle inputs at the point.

The `Synchronize` method is implemented as follows:
```python
...

    def synchronize(self, time):
        # Check that there is still data left to read
        if len(self.ctlr_data) == 0:
            return

        if time >= self.data['time'][0]:
            # Set the vehicle inputs at that time point
            self.steering = self.data['steering'][0]
            self.throttle = self.data['throttle'][0]
            self.braking = self.data['braking'][0]

            # Remove that row in the data
            self.data = np.delete(self.data, 0, axis=0)
...
```

That's basically all the logic we need. The `Advance` method doesn't actually need anything else, so we can just leave it as before!

## Creating our Main Method

We'll now create our main function to actually run our demo. We'll visualize the simulation using `matplotlib` and keep everything else rather simple.

In `custom_controller_demo.py`, underneath your custom controller, add the following:
```python
def main():
    # Create the system
    sys = wa.WASystem(step_size=1e-3)

    # Create the vehicle inputs object
    veh_inputs = wa.WAVehicleInputs()

    # Create an vehicle using a premade vehicle description
    veh_filename = wa.WALinearKinematicBicycle.GO_KART_MODEL_FILE
    veh = wa.WALinearKinematicBicycle(sys, veh_inputs, veh_filename)

    # Visualize the simulation using matplotlib
    vis = wa.WAMatplotlibVisualization(sys, veh, veh_inputs)

    # Create our custom controller!
    ctr = CustomCSVController(sys, veh_inputs, 'controller_data.csv')

    # Instantiate the simulation manager
    sim = wa.WASimulationManager(sys, veh, vis, ctr)

    # Run the simulation
    sim.run()

# Will call the main function when 'python custom_controller_demo.py' is run
if __name__ == "__main__":
    main()
```

## Putting it All Together

Your `controller_data.csv` should look like this:
```
time,steering,throttle,braking
0,0,0.1,0
1,1,0.1,0
5,-1,0.1,0
7.5,-1,1,0
10,0,0,1
```

Your `custom_controller_demo.py` should look like this:
```python

import wa_simulator as wa
import numpy as np


class CustomCSVController(wa.WAController):
    """Simple controller that controls the car from data in a csv file"""

    def __init__(self, sys, veh_inputs, csv_file):
        super().__init__(sys, veh_inputs)  # Calls the WAController's constructor

        self.csv_file = csv_file

        # to be implemented next
        self.ctlr_data = self.read_file(self.csv_file)

    def read_file(self, file):
        # a delimiter is the thing that separates each data value in a row
        # data is now a numpy array with our data
        data = np.genfromtxt(file, delimiter=',', names=True)

        # Errors may occur with the above method, like if delimiter is wrong or inconsistent names

        # Check to make sure the data is as we expected
        if data.dtype.names != ('time', 'steering', 'throttle', 'braking') or np.isnan([r.tolist() for r in data]).any():
            raise ValueError('The csv file is not structured incorrectly!')

        return data

    def synchronize(self, time):
        super().synchronize(time)

        # Check that there is still data left to read
        if len(self.ctlr_data) == 0:
            return

        if time >= self.ctlr_data['time'][0]:
            # Set the vehicle inputs at that time point
            self.steering = self.ctlr_data['steering'][0]
            self.throttle = self.ctlr_data['throttle'][0]
            self.braking = self.ctlr_data['braking'][0]

            # Remove that row in the ctlr_data
            self.ctlr_data = np.delete(self.ctlr_data, 0, axis=0)

    def advance(self, step):
        pass

    def is_ok(self):
        # Will just always return true
        return True


def main():
    # Create the system
    sys = wa.WASystem(step_size=1e-3)

    # Create the vehicle inputs object
    veh_inputs = wa.WAVehicleInputs()

    # Create an vehicle using a premade vehicle description
    veh_filename = wa.WALinearKinematicBicycle.GO_KART_MODEL_FILE
    veh = wa.WALinearKinematicBicycle(sys, veh_inputs, veh_filename)

    # Visualize the simulation using matplotlib
    vis = wa.WAMatplotlibVisualization(sys, veh, veh_inputs, plotter_type='multi')

    # Create our custom controller!
    ctr = CustomCSVController(sys, veh_inputs, 'controller_data.csv')

    # Instantiate the simulation manager
    sim = wa.WASimulationManager(sys, veh, vis, ctr)

    # Run the simulation
    sim.run()


# Will call the main function when 'python custom_controller_demo.py' is run
if __name__ == "__main__":
    main()

```

To run the demo, run:
```shell
python custom_controller_demo.py
```

You can also find the [code in our github repo](https://github.com/WisconsinAutonomous/wa_simulator/blob/master/tutorials/wa_custom_controller/custom_controller_demo.py).

A matplotlib window should pop up and the vehicle should move as we expect!

## Next Steps

You should now have a good understanding of how a controller is made in `wa_simulator`. Feel free to edit this demo or add your own logic! Happy coding!

## Support

Contact [Aaron Young](mailto:aryoung5@wisc.edu) for any questions or concerns regarding the contents of this repository.

## See Also

Follow us on [Facebook](https://www.facebook.com/wisconsinautonomous/), [Instagram](https://www.instagram.com/wisconsinautonomous/), and [LinkedIn](https://www.linkedin.com/company/wisconsin-autonomous/about/)!

<br>

<div>
	<img src="https://github.com/WisconsinAutonomous/wa-resources/blob/master/Images/WA.png?raw=true" alt="Wisconsin Autonomous Logo" class="readme-img" height="100px">  
	<img src="https://github.com/WisconsinAutonomous/wa-resources/blob/master/Images/UWCrest.png?raw=true" alt="University of Wisconsin - Madison Crest" class="readme-img" height="100px" align="right">
</div>
