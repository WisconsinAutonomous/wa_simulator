# Simple chrono demo
# Meant to demonstrate Python API
# PLEASE DON'T CHANGE
# -----------------------------------------------------------------

# Import the simulator
import wa_simulator.chrono as wa

# Command line arguments
parser = wa.WAArgumentParser(use_sim_defaults=True)
args = parser.parse_args()


def main():
    # ---------------
    # Create a system
    # Systems describe simulation settings and can be used to
    # update dynamics
    sys = wa.WAChronoSystem(args.step_size, args.render_step_size)

    # ---------------------
    # Create an environment
    # An environment handles external assets (trees, barriers, etc.) and terrain characteristics
    # Pre-made evGrand Prix (EGP) env file
    env_filename = wa.WAChronoEnvironment.EGP_ENV_MODEL_FILE
    env = wa.WAChronoEnvironment(env_filename, sys)

    # ----------------
    # Create a vehicle
    # Pre-made go kart veh file
    veh_filename = wa.WAChronoVehicle.GO_KART_MODEL_FILE
    veh = wa.WAChronoVehicle(veh_filename, sys, env,
                             initLoc=wa.chrono.ChVectorD(49.8, 132.9, 0.5))

    # -------------
    # Create a Path
    # Load data points from a csv file and interpolate a path
    filename = wa.get_wa_data_file("paths/sample_medium_loop.csv")
    points = wa.load_waypoints_from_csv(filename, delimiter=",")
    path = wa.WASplinePath(points, num_points=1000, is_closed=True)

    # ----------------------
    # Create a visualization
    # Will use irrlicht or matplotlib for visualization
    vis = None
    if args.irrlicht:
        # Draw the path in irrlicht
        wa.draw_path_in_irrlicht(path, sys)  # Display in irrlicht

        # Create spheres representing the sentinel and target on the path
        sentinel_sphere = wa.create_sphere_in_irrlicht(sys, rgb=(1, 0, 0))
        target_sphere = wa.create_sphere_in_irrlicht(sys, rgb=(0, 1, 0))

        vis = irr = wa.WAChronoIrrlicht(veh, sys)
    if args.matplotlib:
        vis = mat = wa.WAMatplotlibVisualization(
            veh, sys, plotter_type="multi")
        vis.plot(path.x, path.y)  # Plot in matplotlib
    if args.irrlicht and args.matplotlib:
        vis = wa.WAMultipleVisualizations([irr, mat])

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

        if args.irrlicht:
            # Update the position of the spheres
            wa.update_position_of_sphere(
                target_sphere, ctr.lat_controller.target)
            wa.update_position_of_sphere(
                sentinel_sphere, ctr.lat_controller.sentinel)


if __name__ == "__main__":
    main()