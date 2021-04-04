# Simple bicycle model demo
# Meant to demonstrate the WA Simulator API
# -----------------------------------------

# Import the simulator
import wa_simulator as wa

# Command line arguments
parser = wa.WAArgumentParser(use_sim_defaults=True)
parser.add_argument("-mv", "--matplotlib", action="store_true", help="Use matplotlib to visualize", default=False)
args = parser.parse_args()


def main():
    # ---------------
    # Create a system
    # Systems describe simulation settings and can be used to
    # update dynamics
    system = wa.WASystem(args=args)

    # --------------------------------
    # Create the vehicle inputs object
    # This is a shared object between controllers, visualizations and vehicles
    vehicle_inputs = wa.WAVehicleInputs()

    # ----------------
    # Create a vehicle
    # Pre-made go kart veh file located in the data directory
    veh_filename = wa.WALinearKinematicBicycle.GO_KART_MODEL_FILE
    vehicle = wa.WALinearKinematicBicycle(system, vehicle_inputs, veh_filename)

    # ----------------------
    # Create a visualization
    # Will use matplotlib for visualization
    visualization = None
    if args.matplotlib:
        visualization = wa.WAMatplotlibVisualization(system, vehicle, vehicle_inputs, plotter_type="multi")
    else:
        print("No visualization selected. To visualize using matplotlib, please pass -mv or --matplotlib as a command line argument.")

    # -------------------
    # Create a controller
    # Will be an interactive controller where the arrow can be used to control the car
    # Must run it from the terminal
    if args.matplotlib:
        controller = wa.WAMatplotlibController(system, vehicle_inputs, visualization)
    else:
        controller = None
        print('Matplotlib is set to off. No controller will be used.')

    # --------------------------
    # Create a simuation wrapper
    # Will be responsible for actually running the simulation
    sim_manager = wa.WASimulationManager(system, vehicle, visualization, controller)

    # ---------------
    # Simulation loop
    step_size = system.step_size
    while sim_manager.is_ok():
        time = system.time

        sim_manager.synchronize(time)
        sim_manager.advance(step_size)


if __name__ == "__main__":
    main()
