# Path follower using a chrono vehicle model
# Meant to demonstrate the WA Simulator API
# -----------------------------------------

# Import the simulator
import wa_simulator.chrono as wa

# Import the controller
from pid_controller import PIDController

# Command line arguments
parser = wa.WAArgumentParser(use_sim_defaults=True)
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

    # ----------------------
    # Create a visualization

    # It's nice to visualize the "look ahead" points for the controller
    # Add two spheres/dots for that purpose
    position = wa.WAVector()
    size = wa.WAVector([0.1, 0.1, 0.1])
    kwargs = {'position': position, 'size': size, 'body_type': 'sphere', 'updates': True}
    sentinel_sphere = environment.create_body(name='sentinel', color=wa.WAVector([1, 0, 0]), **kwargs)
    target_sphere = environment.create_body(name='target', color=wa.WAVector([0, 1, 0]), **kwargs)

    # Will use irrlicht, sensor or matplotlib for visualization
    visualizations = []
    if args.irrlicht:
        irr = wa.WAChronoIrrlicht(system, vehicle, vehicle_inputs, environment=environment)
        visualizations.append(irr)

    if args.sensor:
        sens = wa.WAChronoSensorVisualization(system, vehicle, vehicle_inputs, environment=environment)
        visualizations.append(sens)

    if args.matplotlib:
        mat = wa.WAMatplotlibVisualization(system, vehicle, vehicle_inputs,
                                           environment=environment, plotter_type="multi")
        visualizations.append(mat)

    if len(visualizations) == 0:
        print("No visualization selected. Use -mv, -iv and/or -sv to visualize with matplotlib, irrlicht and/or sensor.")

    # -------------------
    # Create a controller
    # Create a pid controller
    controller = PIDController(system, vehicle, vehicle_inputs, path)
    controller.get_long_controller().set_target_speed(7.5)
    controller.get_long_controller().set_gains(0.1, 0, 1e-2)

    # --------------------------
    # Create a simuation wrapper
    # Will be responsible for actually running the simulation
    sim_manager = wa.WASimulationManager(system, environment, vehicle, *visualizations, controller)

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
