# Simple chrono demo
# Places a GPS and IMU on the vehicle
# Also adds a lidar and camera to the vehicle
# Meant to demonstrate the WA Simulator API
# -----------------------------------------

# Import the simulator
import wa_simulator.chrono as wa

# Check if chrono sensor is found
if wa.missing_chrono_sensor:
    print('WARNING: This demo requires Chrono::Sensor, which requires building chrono from source. Please consult Aaron Young (aryoung5@wisc.edu) with questions.')
    print('If you are a member of Wisconsin Autonomous, consider using the work station. See TODO ADD LINK TO POST')
    print('Exiting...')
    exit()

# Command line arguments
parser = wa.WAArgumentParser(use_sim_defaults=True)

parser.add_argument("-mv", "--matplotlib", action="store_true", help="Use matplotlib to visualize", default=False)
parser.add_argument("-iv", "--irrlicht", action="store_true", help="Use irrlicht to visualize", default=False)

parser.add_argument("-nc", "--no_camera", action="store_true", help="Don't add a camera sensor to the manager", default=False)  # noqa
parser.add_argument("-nl", "--no_lidar", action="store_true", help="Don't add a lidar sensor to the manager", default=False)  # noqa
parser.add_argument("-q", "--quiet", action="store_true", help="Silence any terminal output", default=False)  # noqa

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
    env_filename = "chrono_environment.json"
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
    visualizations = []
    if args.irrlicht:
        irr = wa.WAChronoIrrlicht(system, vehicle, vehicle_inputs, environment=environment)
        irr.bind()  # must be called explicitly or a segmentation fault will happen. Only happens with sensors and irrlicht is used together
        visualizations.append(irr)
    if args.matplotlib:
        mat = wa.WAMatplotlibVisualization(system, vehicle, vehicle_inputs,
                                           environment=environment, plotter_type="single")
        visualizations.append(mat)

    # -------------------
    # Create some sensors
    # A sensor manager is responsible for different sensors
    # Use a pre-made "sensor suite" file that describes the different sensors we want to load
    # NOTE: Must come after initialization of the visualizers

    scene_filename = wa.WAChronoSensorManager.EGP_SENSOR_SCENE_FILE
    sens_manager = wa.WAChronoSensorManager(system, scene_filename)

    imu_filename = wa.WAIMUSensor.SBG_IMU_SENSOR_FILE
    imu = wa.load_sensor_from_json(system, imu_filename, vehicle=vehicle)
    sens_manager.add_sensor(imu)

    gps_filename = wa.WAGPSSensor.SBG_GPS_SENSOR_FILE
    gps = wa.load_sensor_from_json(system, gps_filename, vehicle=vehicle)
    sens_manager.add_sensor(gps)

    camera = None
    if not args.no_camera:
        cam_filename = wa.WAChronoSensor.MONO_CAM_SENSOR_FILE
        camera = wa.load_chrono_sensor_from_json(system, cam_filename, vehicle=vehicle)
        sens_manager.add_sensor(camera)

    lidar = None
    if not args.no_lidar:
        ldr_filename = wa.WAChronoSensor.LDMRS_LIDAR_SENSOR_FILE
        lidar = wa.load_chrono_sensor_from_json(system, ldr_filename, vehicle=vehicle)
        sens_manager.add_sensor(lidar)

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
    sim_manager = wa.WASimulationManager(system, environment, vehicle, *visualizations, controller, sens_manager)

    # ---------------
    # Simulation loop
    step_size = system.step_size
    render_steps = 0.0
    render_rate = 1 / 30  # 30 Hz
    while sim_manager.is_ok():
        time = system.time

        sim_manager.synchronize(time)
        sim_manager.advance(step_size)

        if time > render_steps:
            # Get the data
            acceleration, angular_velocity, orientation = imu.get_data()
            coord = gps.get_data()
            if camera is not None:
                image = camera.get_data()  # get the image data
            if lidar is not None:
                pointcloud = lidar.get_data()  # get the point cloud data

            if not args.quiet:
                v = 20  # Formatting

                print(f'[{round(time,2)}] ::')
                print('\tAcceleration:'.ljust(v), acceleration)
                print('\tAngular Velocity:'.ljust(v), angular_velocity)
                print('\tOrientation:'.ljust(v), orientation)
                print(f'\tGPS:'.ljust(v), coord)
                print()

            render_steps += render_rate


if __name__ == "__main__":
    main()
