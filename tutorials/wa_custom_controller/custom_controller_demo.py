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
