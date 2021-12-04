# Simple demo to showcase how to communicate with an external entity using message passing
# Meant to demonstrate the WA Simulator API
# -----------------------------------------

# Import the simulator
import wa_simulator as wa

# Command line arguments
parser = wa.WAArgumentParser(use_sim_defaults=True)
args = parser.parse_args()


def vehicle_parser(element: list, message: dict):
    """Custom parser method to populate a position list

    Will be called everytime a vehicle message is received

    Args:
        element (list): The reference to the list object that can be updated
        message (dict): The received message
    """
    x,y,z = message["data"]["position"].xyz
    element[0] = x
    element[1] = y
    element[2] = z

def main():
    # ---------------
    # Create a system
    system = wa.WASystem(args=args)

    # --------------------------------
    # Create the vehicle inputs object
    vehicle_inputs = wa.WAVehicleInputs(throttle=1)

    # --------------------------------
    # Create the vehicle position list
    # The vehicle position list that will be updated throughout the simulation
    vehicle_position = [0,0,0]

    # -----------------
    # Create the bridge
    # The bridge is responsible for communicating the simulation
    # It will receive vehicle state and then send vehicle inputs to change the simulationi
    bridge = wa.WABridge(system, hostname="0.0.0.0", port=5555, server=False)
    bridge.add_sender("vehicle_inputs", vehicle_inputs)
    bridge.add_receiver("vehicle", vehicle_position, message_parser=vehicle_parser)

    # --------------------------
    # Create a simulation wrapper
    # Will be responsible for actually running the simulation
    sim_manager = wa.WASimulationManager(system, bridge)

    # ---------------
    # Simulation loop
    step_size = system.step_size
    while sim_manager.is_ok():
        time = system.time

        sim_manager.synchronize(time)
        sim_manager.advance(step_size)

        print(vehicle_position)

if __name__ == "__main__":
    main()
