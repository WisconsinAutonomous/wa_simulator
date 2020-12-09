# Simple chrono demo
# Meant to demonstrate Python API
# PLEASE DON'T CHANGE
# -----------------------------------------------------------------

# Import the simulator
import wa_simulator.chrono as wa

# Simulation step size
step_size = 3e-3 # [s]

def main():
    # ---------------
    # Create a system
    # Systems describe simulation settings and can be used to 
    # update dynamics
    sys = wa.WAChronoSystem(step_size)

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
    irr = wa.WAChronoIrrlicht(veh, sys)
    mat = wa.WAMatplotlibVisualization(veh, sys)
    vis = wa.WAMultipleVisualizations([irr, mat])

    # -------------------
    # Create a controller
    # Will be an interactive controller where WASD can be used to control the car
    ctr = wa.WAIrrlichtController(irr, sys)

    # --------------------------
    # Create a simuation wrapper
    # Will be responsible for actually running the simulation
    sim = wa.WASimulation(sys, env, veh, vis, ctr)

    # ---------------
    # Simulation loop
    while True:
        time = sys.GetSimTime()

        sim.Synchronize(time)
        sim.Advance(step_size)

if __name__ == "__main__":
    main()