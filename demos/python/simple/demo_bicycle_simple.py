# Simple chrono demo
# Meant to demonstrate Python API
# PLEASE DON'T CHANGE
# -----------------------------------------------------------------

# Import the simulator
import wa_simulator as wa

# Simulation step size
step_size = 3e-3 # [s]

def main():
    # ---------------
    # Create a system
    # Systems describe simulation settings and can be used to 
    # update dynamics
    sys = wa.WASystem(step_size)

    # ---------------------
    # Create an environment
    # An environment handles external assets (trees, barriers, etc.) and terrain characteristics
    env_filename = wa.WASimpleEnvironment.EGP_ENV_MODEL_FILE # Pre-made evGrand Prix (EGP) env file
    env = wa.WASimpleEnvironment(env_filename, sys)

    # ----------------
    # Create a vehicle
    veh_filename = wa.WALinearKinematicBicycle.GO_KART_MODEL_FILE # Pre-made go kart veh file
    veh = wa.WALinearKinematicBicycle(veh_filename)

    # ----------------------
    # Create a visualization
    # Will use matplotlib for visualization
    vis = wa.WAMatplotlibVisualization(veh, sys)

    # -------------------
    # Create a controller
    # Will be an interactive controller where the arrow can be used to control the car
    # Must run it from the terminal
    # ctr = wa.WAKeyboardController(sys)
    ctr = wa.WASimpleController()

    # --------------------------
    # Create a simuation wrapper
    # Will be responsible for actually running the simulation
    sim = wa.WASimulation(sys, env, veh, vis, ctr)

    # ---------------
    # Simulation loop
    while True:
        time = sys.GetSimTime()

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
        sim.Advance(step_size)

        sim.Record('bicycle_simple.csv')

if __name__ == "__main__":
    main()