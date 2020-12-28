# Simple chrono demo
# Meant to demonstrate Python API
# PLEASE DON'T CHANGE
# -----------------------------------------------------------------

# Import the simulator
import wa_simulator.chrono as wa

# Command line arguments
parser = wa.WAArgumentParser(use_defaults=True)
controller_group = parser.add_mutually_exclusive_group(required=True)
controller_group.add_argument('-ic', '--irrlicht_controller', action='store_true', help='Use Irrlicht Controller', default=False)
controller_group.add_argument('-sc', '--simple_controller', action='store_true', help='Use Simple Controller', default=False)
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
    env_filename = wa.WAChronoEnvironment.EGP_ENV_MODEL_FILE # Pre-made evGrand Prix (EGP) env file
    env = wa.WAChronoEnvironment(env_filename, sys)

    # ----------------
    # Create a vehicle
    veh_filename = wa.WAChronoVehicle.GO_KART_MODEL_FILE # Pre-made go kart veh file
    veh = wa.WAChronoVehicle(veh_filename, sys, env)

    # ----------------------
    # Create a visualization
    # Will use matplotlib and irrlicht for visualization
    if args.irrlicht:
        vis = wa.WAChronoIrrlicht(veh, sys)
    elif args.matplotlib:
        vis = wa.WAMatplotlibVisualization(veh, sys)
    else:
        vis = None

    # -------------------
    # Create a controller
    # Will be an interactive controller where WASD can be used to control the car
    if args.irrlicht_controller:
        if not args.irrlicht:
            raise RuntimeError('To use the irrlicht controller, you must use an irrlicht visualization. Pass in \'iv\' to achieve this.')
        ctr = wa.WAIrrlichtController(vis, sys)
    else:
        ctr = wa.WASimpleController()

    # --------------------------
    # Create a simuation wrapper
    # Will be responsible for actually running the simulation
    sim = wa.WASimulation(sys, env, veh, vis, ctr, 'chrono_simple.csv' if args.record else None)

    # ---------------
    # Simulation loop
    while sim.IsOk():
        time = sys.GetSimTime()

        if args.simple_controller:
            if time < 5:
                ctr.steering = 0
                ctr.throttle = 0.2
                ctr.braking = 0
            elif time < 10:
                ctr.steering = 0.5
                ctr.throttle = 0.1
                ctr.braking = 0
            elif time < 20:
                ctr.steering = -0.75
                ctr.throttle = 0.3
                ctr.braking = 0
            else:
                break

        sim.Synchronize(time)
        sim.Advance(args.step_size)

if __name__ == "__main__":
    main()