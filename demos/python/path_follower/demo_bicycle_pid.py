# Simple chrono demo
# Meant to demonstrate Python API
# PLEASE DON'T CHANGE
# -----------------------------------------------------------------

# Import the simulator
import wa_simulator as wa

# Command line arguments
parser = wa.WAArgumentParser(use_sim_defaults=True)
args = parser.parse_args()


def main():
    # ---------------
    # Create a system
    # Systems describe simulation settings and can be used to
    # update dynamics
    sys = wa.WASystem(args.step_size, args.render_step_size)

    # ---------------------
    # Create an environment
    # An environment handles external assets (trees, barriers, etc.) and terrain characteristics
    # Pre-made evGrand Prix (EGP) env file
    env_filename = wa.WASimpleEnvironment.EGP_ENV_MODEL_FILE
    env = wa.WASimpleEnvironment(env_filename, sys)

    # ----------------
    # Create a vehicle
    # Pre-made go kart veh file
    veh_filename = wa.WALinearKinematicBicycle.GO_KART_MODEL_FILE
    veh = wa.WALinearKinematicBicycle(veh_filename, x=49.8, y=132.9)

    # ----------------------
    # Create a visualization
    # Will use matplotlib for visualization
    vis = wa.WAMatplotlibVisualization(veh, sys, plotter_type="multi")

    # -------------
    # Create a Path
    # Load data points from a csv file and interpolate a path
    filename = wa.get_wa_data_file("paths/sample_medium_loop.csv")
    points = wa.load_waypoints_from_csv(filename, delimiter=",")
    path = wa.WASplinePath(points, num_points=1000, is_closed=True)

    vis.plot(path.x, path.y)

    # -------------------
    # Create a controller
    # Create a pid controller
    ctr = wa.WAPIDController(sys, veh, path)

    # --------------------------
    # Create a simuation wrapper
    # Will be responsible for actually running the simulation
    sim = wa.WASimulation(
        sys, env, veh, vis, ctr, "bicycle_simple.csv" if args.record else None
    )

    # ---------------
    # Simulation loop
    while sim.is_ok():
        time = sys.get_sim_time()

        sim.synchronize(time)
        sim.advance(args.step_size)


if __name__ == "__main__":
    main()