# Path follower using a simple bicycle model
# Meant to demonstrate the WA Simulator API
# -----------------------------------------

# Import the simulator
import wa_simulator as wa

# Import the controller
from pid_controller import PIDController

# Command line arguments
parser = wa.WAArgumentParser(use_sim_defaults=True)
args = parser.parse_args()


def main():
    # ---------------
    # Create a system
    # System's handle the simulation settings
    system = wa.WASystem(args=args)

    # ---------------------------
    # Create a simple environment
    # Environment will create a track like path for the vehicle
    env_filename = wa.WASimpleEnvironment.EGP_ENV_MODEL_FILE
    environment = wa.WASimpleEnvironment(system, env_filename)

    # --------------------------------
    # Create the vehicle inputs object
    # This is a shared object between controllers, visualizations and vehicles
    vehicle_inputs = wa.WAVehicleInputs()

    # ----------------
    # Create a vehicle
    # Uses a premade json specification file that describes the properties of the vehicle
    init_pos = wa.WAVector([49.8, 132.9, 0.5])
    veh_filename = wa.WALinearKinematicBicycle.GO_KART_MODEL_FILE
    vehicle = wa.WALinearKinematicBicycle(system, vehicle_inputs, veh_filename, init_pos=init_pos)

    # -------------
    # Create a Path
    # Load data points from a csv file and interpolate a path
    filename = wa.get_wa_data_file("paths/sample_medium_loop.csv")
    points = wa.load_waypoints_from_csv(filename, delimiter=",")
    path = wa.WASplinePath(points, num_points=1000, is_closed=True)

    # ----------------------
    # Create a visualization
    # Will use matplotlib for visualization
    visualization = wa.WAMatplotlibVisualization(
        system, vehicle, vehicle_inputs, environment=environment, plotter_type="multi")

    # -------------------
    # Create a controller
    # Create a pid controller
    controller = PIDController(system, vehicle, vehicle_inputs, path)

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
