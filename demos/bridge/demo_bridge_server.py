# Simple demo to showcase how to communicate with an external entity using message passing
# Meant to demonstrate the WA Simulator API
# -----------------------------------------

# Import the simulator
import wa_simulator as wa

# Other imports
import os

# Command line arguments
parser = wa.WAArgumentParser(use_sim_defaults=True)
args = parser.parse_args()

if os.environ.get("DOCKER_ENV"):
    wa.set_wa_data_directory('/root/data/')

def main():
    # ---------------
    # Create a system
    # Systems describe simulation settings and can be used to
    # update dynamics
    system = wa.WASystem(args=args)

    # --------------------------------
    # Create the vehicle inputs object
    # This is a shared object between controllers, visualizations and vehicles
    vehicle_inputs = wa.WAVehicleInputs()

    # ----------------
    # Create a vehicle
    # Pre-made go kart veh file located in the data directory
    veh_filename = wa.WALinearKinematicBicycle.GO_KART_MODEL_FILE
    vehicle = wa.WALinearKinematicBicycle(system, vehicle_inputs, veh_filename)

    # ----------------------
    # Create a visualization
    visualization = None
    # visualization = wa.WAMatplotlibVisualization(system, vehicle, vehicle_inputs, plotter_type="single")

    # -------------------
    # Create a controller
    # Will be an interactive controller where the arrow can be used to control the car
    # Must run it from the terminal
    controller = None
    if visualization is not None:
        controller = wa.WAMatplotlibController(system, vehicle_inputs, visualization)

    # -------------------
    # Create some sensors
    # A sensor manager is responsible for different sensors
    sens_manager = wa.WASensorManager(system)

    gps_filename = wa.WAGPSSensor.SBG_GPS_SENSOR_FILE
    gps = wa.load_sensor_from_json(system, gps_filename, vehicle=vehicle)
    sens_manager.add_sensor(gps)

    imu_filename = wa.WAIMUSensor.SBG_IMU_SENSOR_FILE
    imu = wa.load_sensor_from_json(system, imu_filename, vehicle=vehicle)
    sens_manager.add_sensor(imu)

    # -----------------
    # Create the bridge
    # The bridge is responsible for sending the data out of the simulation to an external stack
    # Will send out vehicle state information, and receive vehicle_inputs to control the car
    bridge = wa.WABridge(system, hostname="0.0.0.0")
    bridge.add_sender("vehicle", vehicle)
    bridge.add_sender("gps", gps)
    bridge.add_sender("imu", imu)
    bridge.add_receiver("vehicle_inputs", vehicle_inputs)

    # --------------------------
    # Create a simulation wrapper
    # Will be responsible for actually running the simulation
    sim_manager = wa.WASimulationManager(system, vehicle, visualization, controller, bridge, sens_manager)

    # ---------------
    # Simulation loop
    step_size = system.step_size
    while sim_manager.is_ok():
        time = system.time

        sim_manager.synchronize(time)
        sim_manager.advance(step_size)

if __name__ == "__main__":
    main()
