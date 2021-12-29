# Simple demo to showcase how to communicate with an external entity using message passing
# Meant to demonstrate the WA Simulator API
# -----------------------------------------

# Import the simulator
import wa_simulator as wa

# Import the controller
from pid_controller import PIDController

# Other imports
import os

# Command line arguments
parser = wa.WAArgumentParser(use_sim_defaults=True)

group = parser.add_mutually_exclusive_group()
group.add_argument("-mv", action="store_true", help="Visualize the simulation using Matplotlib")
group.add_argument("-mb", action="store_true", help="Communicate Matplotlib visualizer over bridge")

args = parser.parse_args()

if os.environ.get("DOCKER_ENV"):
    wa.set_wa_data_directory('/root/data/')

def main():
    # ---------------
    # Create a system
    # Systems describe simulation settings and can be used to
    # update dynamics
    system = wa.WASystem(args=args)

    # ---------------------------
    # Create a simple environment
    # Environment will create a track like path for the vehicle
    env_filename = wa.WASimpleEnvironment.EGP_ENV_MODEL_FILE
    environment = wa.WASimpleEnvironment(system, env_filename)

    # ----------------
    # Create the track
    # Create it from a json specification file
    filename = wa.get_wa_data_file("tracks/sample_medium_loop.json")
    track = wa.create_track_from_json(filename)

    # --------------------------------
    # Create the vehicle inputs object
    # This is a shared object between controllers, visualizations and vehicles
    vehicle_inputs = wa.WAVehicleInputs()

    # ----------------
    # Create a vehicle
    # Pre-made go kart veh file located in the data directory
    init_pos = wa.WAVector([49.8, 132.9, 0.5])
    veh_filename = wa.WALinearKinematicBicycle.GO_KART_MODEL_FILE
    vehicle = wa.WALinearKinematicBicycle(system, vehicle_inputs, veh_filename, init_pos=init_pos)

    # ----------------------
    # Create a visualization
    visualizations = []
    if args.mv:
        matplotlib_visualization = wa.WAMatplotlibVisualization(system, vehicle, vehicle_inputs, environment=environment, plotter_type="multi")
        visualizations.append(matplotlib_visualization)
    if args.mb:
        bridge_visualization = wa.WAMatplotlibVisualization(system, vehicle, vehicle_inputs, environment=environment, plotter_type="bridge")
        visualizations.append(bridge_visualization)

    # -------------------
    # Create a controller
    # Will be an interactive controller where the arrow can be used to control the car
    # Must run it from the terminal
    controller = PIDController(system, vehicle, vehicle_inputs, track.center)
    
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
    bridge = wa.WABridge(system, hostname="0.0.0.0", port=5555)
    bridge.add_sender("vehicle", vehicle)
    bridge.add_sender("gps", gps)
    bridge.add_sender("imu", imu)
    if args.mb:
        bridge.add_sender("visualization", bridge_visualization)
    bridge.add_sender("track", track, vehicle=vehicle, fov=30, detection_range=100)
    bridge.add_receiver("vehicle_inputs", vehicle_inputs)

    # --------------------------
    # Create a simulation wrapper
    # Will be responsible for actually running the simulation
    sim_manager = wa.WASimulationManager(system, vehicle, *visualizations, controller, bridge, environment, sens_manager)

    # ---------------
    # Simulation loop
    step_size = system.step_size
    while sim_manager.is_ok():
        time = system.time

        sim_manager.synchronize(time)
        sim_manager.advance(step_size)

if __name__ == "__main__":
    main()
