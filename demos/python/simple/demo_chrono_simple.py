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
    veh = wa.WAChronoVehicle(veh_filename, sys, env)

    # ----------------------
    # Create a visualization
    # Will use matplotlib and irrlicht for visualization
    vis = None
    if args.irrlicht:
        vis = irr = wa.WAChronoIrrlicht(veh, sys)
    if args.matplotlib:
        vis = mat = wa.WAMatplotlibVisualization(
            veh, sys, plotter_type="multi")
    if args.irrlicht and args.matplotlib:
        vis = wa.WAMultipleVisualizations([irr, mat])

    # -------------------
    # Create a controller
    # Will be an interactive controller
    if args.matplotlib:
        ctr = wa.WAMatplotlibController(sys, mat)
    elif args.irrlicht:
        ctr = wa.WAIrrlichtController(irr, sys)
    else:
        ctr = wa.WATerminalKeyboardController(sys)

    # --------------------------
    # Create a simuation wrapper
    # Will be responsible for actually running the simulation
    sim = wa.WASimulation(
        sys, env, veh, vis, ctr, "chrono_simple.csv" if args.record else None
    )

    # ---------------
    # Simulation loop
    while sim.is_ok():
        time = sys.get_sim_time()

        sim.synchronize(time)
        sim.advance(args.step_size)


if __name__ == "__main__":
    main()
