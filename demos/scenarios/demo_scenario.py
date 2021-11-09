# Path follower using a simple bicycle model
# Meant to demonstrate the WA Simulator API
# -----------------------------------------

# Import the simulator
import wa_simulator as wa

# Command line arguments
parser = wa.WAArgumentParser(use_sim_defaults=True)
args = parser.parse_args()


def main():
    # ---------------
    # Create a system
    # System's handle the simulation settings
    system = wa.WASystem(args=args)

    # -----------------
    # Create a scenario
    # Scenario's handle the world for which the simulation runs
    # Can handle dynamic attributes, as well as static
    filename = "ev_grand_prix.json"
    scenario = wa.WAScenarioManager(system, filename)

    # --------------------------
    # Create a simuation wrapper
    # Will be responsible for actually running the simulation
    sim_manager = wa.WASimulationManager(system, scenario)

    # ---------------
    # Simulation loop
    step_size = system.step_size
    while sim_manager.is_ok():
        time = system.time

        sim_manager.synchronize(time)
        sim_manager.advance(step_size)


if __name__ == "__main__":
    main()
