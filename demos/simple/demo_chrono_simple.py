# Simple chrono demo
# Meant to demonstrate the WA Simulator API
# -----------------------------------------------------------------

# Import the simulator
import wa_simulator.chrono as wa

# Command line arguments
parser = wa.WAArgumentParser(use_sim_defaults=True)
parser.add_argument("-mv", "--matplotlib", action="store_true", help="Use matplotlib to visualize", default=False)
parser.add_argument("-iv", "--irrlicht", action="store_true", help="Use irrlicht to visualize", default=False)
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
    veh_filename = wa.WAChronoVehicle.GO_KART_MODEL_FILE
    vehicle = wa.WAChronoVehicle(system, vehicle_inputs, environment, veh_filename)

    # ----------------------
    # Create a visualization
    # Will use matplotlib and irrlicht for visualization
    vis = None
    visualizations = []
    if args.irrlicht:
        irr = wa.WAChronoIrrlicht(system, vehicle, vehicle_inputs)
        visualizations.append(irr)
    if args.matplotlib:
        mat = wa.WAMatplotlibVisualization(system, vehicle, vehicle_inputs, plotter_type="multi")
        visualizations.append(mat)
    if not args.irrlicht and not args.matplotlib:
        print("No visualization selected. Use -iv and/or -mv to visualize with irrlicht and/or matplotlib.")

    # -------------------
    # Create a controller
    # Will be an interactive controller
    if args.matplotlib:
        controller = wa.WAMatplotlibController(system, vehicle_inputs, mat)
    elif args.irrlicht:
        controller = wa.WAIrrlichtController(system, vehicle_inputs, irr)
    else:
        controller = None
        print('Irrlicht and Matplotlib are both set to off. No controller will be used.')

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


if __name__ == "__main__":
    main()
