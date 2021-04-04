# Path follower using a simple bicycle model
# Multiple vehicles are used. The vehicles
# that aren't tracked are considered "opponents"
# Meant to demonstrate the WA Simulator API
# -----------------------------------------

# Import the simulator
import wa_simulator as wa

# Import the controller
from pid_controller import PIDController

# Command line arguments
parser = wa.WAArgumentParser(use_sim_defaults=True)
parser.add_argument("-n", "--num_opponents", type=int,
                    help="Number of opponents to simulation. The more, the less efficient the simulation.", default=2)
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

    # ------------------
    # Create n opponents
    opponents = []
    opponent_vehicle_inputs_list = []
    num_opponents = args.num_opponents
    for i in range(num_opponents):
        opponent_init_pos = wa.WAVector(points[i+1])
        opponent_vehicle_inputs = wa.WAVehicleInputs()
        opponent = wa.WALinearKinematicBicycle(system, opponent_vehicle_inputs,
                                               veh_filename, init_pos=opponent_init_pos)
        opponents.append(opponent)
        opponent_vehicle_inputs_list.append(opponent_vehicle_inputs)

    # ----------------------
    # Create a visualization
    # Will use matplotlib for visualization
    visualization = wa.WAMatplotlibVisualization(
        system, vehicle, vehicle_inputs, environment=environment, plotter_type="multi", opponents=opponents)

    # -------------------
    # Create a controller
    # Create a pid controller
    controllers = [PIDController(system, vehicle, vehicle_inputs, path)]
    for i in range(num_opponents):
        opponent_controller = PIDController(system, opponents[i], opponent_vehicle_inputs_list[i], path)
        controllers.append(opponent_controller)

    # --------------------------
    # Create a simuation wrapper
    # Will be responsible for actually running the simulation
    sim_manager = wa.WASimulationManager(system, vehicle, visualization, *controllers, *opponents)

    # ---------------
    # Simulation loop
    step_size = system.step_size
    while sim_manager.is_ok():
        time = system.time

        sim_manager.synchronize(time)
        sim_manager.advance(step_size)


if __name__ == "__main__":
    main()
