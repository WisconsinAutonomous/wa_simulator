# Simple path demo
# Meant to demonstrate Python API
# PLEASE DON'T CHANGE
# -----------------------------------------------------------------

# Import the simulator
import wa_simulator as wa
import matplotlib.pyplot as plt

# Command line arguments
parser = wa.WAArgumentParser(use_sim_defaults=False)
parser.add_argument(
    "-p",
    "--plot",
    action="store_true",
    help="Plot the paths",
    default=False,
)
args = parser.parse_args()


def main():
    # Load data points from a csv file
    filename = wa.get_wa_data_file("paths/sample_medium_loop.csv")
    points = wa.load_waypoints_from_csv(filename, delimiter=",")

    # Create the path
    path = wa.WASplinePath(points, num_points=1000)

    # Create another path
    points = [[9, 8], [20, 5], [25, 15], [34, 24],
              [35, 28], [70, 18], [130, 98]]
    path2 = wa.WASplinePath(points, num_points=1000, is_closed=False)

    # Plot, if desired
    if args.plot:
        path.plot("k", show=False)
        path2.plot("b", show=True)


if __name__ == "__main__":
    main()
