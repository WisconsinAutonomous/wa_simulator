# Simple bicycle model demo
# Places a GPS and IMU on the vehicle
# Meant to demonstrate the WA Simulator API
# -----------------------------------------

# Import the simulator
import wa_simulator as wa

# Command line arguments
parser = wa.WAArgumentParser(use_sim_defaults=True)
parser.add_argument("-mv", "--matplotlib", action="store_true", help="Use matplotlib to visualize", default=False)
parser.add_argument("-q", "--quiet", action="store_true", help="Silence any terminal output", default=False)
args = parser.parse_args()


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
    # Pre-made go kart veh file
    veh_filename = wa.WALinearKinematicBicycle.GO_KART_MODEL_FILE
    vehicle = wa.WALinearKinematicBicycle(system, vehicle_inputs, veh_filename)

    # ----------------------
    # Create a visualization
    # Will use matplotlib for visualization
    visualization = None
    if args.matplotlib:
        visualization = wa.WAMatplotlibVisualization(system, vehicle, vehicle_inputs, plotter_type="multi")
    else:
        print("No visualization selected. To visualize using matplotlib, please pass -mv or --matplotlib as a command line argument.")

    # -------------------
    # Create a controller
    # Will be an interactive controller where the arrow can be used to control the car
    # Must run it from the terminal
    if args.matplotlib:
        controller = wa.WAMatplotlibController(system, vehicle_inputs, visualization)
    else:
        controller = None
        print('Matplotlib is set to off. No controller will be used.')

    # -------------------
    # Create some sensors
    # A sensor manager is responsible for different sensors
    sens_manager = wa.WASensorManager(system)

    imu_filename = wa.WAIMUSensor.SBG_IMU_SENSOR_FILE
    imu = wa.load_sensor_from_json(system, imu_filename, vehicle=vehicle)
    sens_manager.add_sensor(imu)

    gps_filename = wa.WAGPSSensor.SBG_GPS_SENSOR_FILE
    gps = wa.load_sensor_from_json(system, gps_filename, vehicle=vehicle)
    sens_manager.add_sensor(gps)

    # --------------------------
    # Create a simuation wrapper
    # Will be responsible for actually running the simulation
    sim_manager = wa.WASimulationManager(system, vehicle, visualization, controller, sens_manager)

    # ---------------
    # Simulation loop
    print_steps = 0
    step_size = system.step_size
    while sim_manager.is_ok():
        time = system.time

        sim_manager.synchronize(time)
        sim_manager.advance(step_size)

        if time > print_steps and not args.quiet:
            # Get the data
            acceleration, angular_velocity, orientation = imu.get_data()
            coord = gps.get_data()

            v = 20  # Formatting

            print(f'[{round(time,2)}] ::')
            print('\tAcceleration:'.ljust(v), acceleration)
            print('\tAngular Velocity:'.ljust(v), angular_velocity)
            print('\tOrientation:'.ljust(v), orientation)
            print(f'\tGPS:'.ljust(v), coord)
            print()

            print_steps += 1


if __name__ == "__main__":
    main()
