# Path follower using a chrono vehicle model
# Multiple vehicles are used. The vehicles
# that aren't tracked are considered "opponents"
# Meant to demonstrate the WA Simulator API
# -----------------------------------------

# Import the simulator
import wa_simulator.chrono as wa

# Import the controller
from pid_controller import PIDController

# Command line arguments
parser = wa.WAArgumentParser(use_sim_defaults=True)
parser.add_argument("-n", "--num_opponents", type=int,
                    help="Number of opponents to simulation. The more, the less efficient the simulation.", default=2)
parser.add_argument("-mv", "--matplotlib", action="store_true", help="Use matplotlib to visualize", default=False)
parser.add_argument("-iv", "--irrlicht", action="store_true", help="Use irrlicht to visualize", default=False)
parser.add_argument("-sv", "--sensor", action="store_true", help="Use sensor to visualize", default=False)
args = parser.parse_args()


def main():
    # ---------------
    # Create a system
    # Systems describe simulation settings and can be used to
    # update dynamics
    system = wa.WAChronoSystem(args=args)

    # ---------------------
    # Create an environment
    # An environment handles external assets (trees, barriers, etc.) and terrain characteristics
    # Pre-made evGrand Prix (EGP) env file
    env_filename = wa.WAChronoEnvironment.EGP_ENV_MODEL_FILE
    environment = wa.WAChronoEnvironment(system, env_filename)

    # --------------------------------
    # Create the vehicle inputs object
    # This is a shared object between controllers, visualizations and vehicles
    vehicle_inputs = wa.WAVehicleInputs()

    # ----------------
    # Create a vehicle
    # Pre-made go kart veh file
    init_loc = wa.WAVector([49.8, 132.9, 0.5])
    veh_filename = wa.WAChronoVehicle.GO_KART_MODEL_FILE
    vehicle = wa.WAChronoVehicle(system, vehicle_inputs, environment, veh_filename, init_loc=init_loc)

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
        opponent_init_loc = wa.WAVector(points[i+1])
        opponent_init_loc.z = 0.1
        opponent_vehicle_inputs = wa.WAVehicleInputs()
        opponent = wa.WAChronoVehicle(system, opponent_vehicle_inputs, environment,
                                      veh_filename, init_loc=opponent_init_loc)

        opponents.append(opponent)
        opponent_vehicle_inputs_list.append(opponent_vehicle_inputs)

    # ----------------------
    # Create a visualization

    # It's nice to visualize the "look ahead" points for the controller
    # Add two spheres/dots for that purpose
    position = wa.WAVector()
    size = wa.WAVector([0.1, 0.1, 0.1])
    kwargs = {'position': position, 'size': size, 'body_type': 'sphere', 'updates': True}
    sentinel_sphere = environment.create_body(name='sentinel', color=wa.WAVector([1, 0, 0]), **kwargs)
    target_sphere = environment.create_body(name='target', color=wa.WAVector([0, 1, 0]), **kwargs)

    # Will use irrlicht or matplotlib for visualization
    visualizations = []
    if args.irrlicht:
        irr = wa.WAChronoIrrlicht(system, vehicle, vehicle_inputs, environment=environment, opponents=opponents)
        visualizations.append(irr)

    if args.sensor:
        sens = wa.WAChronoSensorVisualization(system, vehicle, vehicle_inputs, environment=environment)
        visualizations.append(sens)

    if args.matplotlib:
        mat = wa.WAMatplotlibVisualization(system, vehicle, vehicle_inputs,
                                           environment=environment, plotter_type="multi", opponents=opponents)
        visualizations.append(mat)

    # -------------------
    # Create a controller
    # Create a pid controller
    controller = PIDController(system, vehicle, vehicle_inputs, path)
    controller.get_long_controller().set_target_speed(9)
    controller.get_long_controller().set_gains(0.1, 0, 1e-2)

    controllers = [controller]
    for i in range(num_opponents):
        opponent_controller = PIDController(system, opponents[i], opponent_vehicle_inputs_list[i], path)
        opponent_controller.get_long_controller().set_target_speed(9)
        opponent_controller.get_long_controller().set_gains(0.1, 0, 1e-2)

        controllers.append(opponent_controller)

    # --------------------------
    # Create a simuation wrapper
    # Will be responsible for actually running the simulation
    sim_manager = wa.WASimulationManager(system, environment, vehicle, *visualizations, *controllers, *opponents)

    # ---------------
    # Simulation loop
    step_size = system.step_size
    while sim_manager.is_ok():
        time = system.time

        sim_manager.synchronize(time)
        sim_manager.advance(step_size)

        # Update the position of the spheres
        target_sphere.position = controller.get_target_pos()
        sentinel_sphere.position = controller.get_sentinel_pos()


if __name__ == "__main__":
    main()
