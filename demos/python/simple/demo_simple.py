# Simple demo class
# Meant to demonstrate Python API
# PLEASE DON'T CHANGE

# Right now, used for planning how the API should work

# -----------------------------------------------------------------

# imports
# ...

# Simulation step size
step_size = 1e-3 # [s]

def main():
    # --------------
    # Create a track
    # --------------
    centerline = WABezierPath()
    track = WATrack(centerline)

    # ---------------------
    # Create an environment
    # ---------------------
    environment = WAEnvironment()

    # ----------------
    # Create a terrain
    # ----------------
    terrain = WATerrain()

    # ----------------
    # Create a vehicle
    # ----------------
    vehicle = WAVehicle()

    # -------------------
    # Create a controller
    # -------------------
    controller = WAController()

    # -----------------------------
    # Create the simulation wrapper
    # -----------------------------
    simulator = WAChronoWrapper()

    # -------------------
    # Simulation loop
    # -------------------
    while simulator.Ok():
        time = simulator.GetSimTime()

        # Update controller and vehicle throttle/steering/braking
        controller.Advance(step_size)

        driver_inputs = controller.GetDriverInputs()
        vehicle.SetDriverInputs(driver_inputs)

        # Advance the simulation by a step
        simulator.Advance(step_size)

        # Synchronize the different simulation elements at the specified time
        simulator.Synchronize(time)

if __name__ == "__main__":
    main()