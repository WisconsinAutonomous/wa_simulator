# Simple path demo
# Meant to demonstrate the WA Simulator API
# -----------------------------------------------------------------

# Import the simulator
import wa_simulator as wa
import matplotlib.pyplot as plt

# Command line arguments
parser = wa.WAArgumentParser(use_sim_defaults=False)
parser.add_argument("-p", "--plot", action="store_true", help="Plot the paths", default=False)
args = parser.parse_args()


def main():
    # Load data points from a csv file
    filename = wa.get_wa_data_file("paths/sample_medium_loop.csv")
    points = wa.load_waypoints_from_csv(filename, delimiter=",") * 2

    # Create the path
    path1 = wa.WASplinePath(points, num_points=1000)

    # Create another path
    points = [[9, 8, 0.5], [20, 5, 0.5], [25, 15, 0.5], [34, 24, 0.5],
              [35, 28, 0.5], [70, 18, 0.5], [130, 98, 0.5]]
    path2 = wa.WASplinePath(points, num_points=1000, is_closed=False)

    # Create a third path using a json
    filename = wa.get_wa_data_file("paths/sample_medium_loop.json")
    path3 = wa.create_path_from_json(filename)

    # Plot, if desired
    if args.plot:
        path1.plot("k", show=False)
        path2.plot("b", show=False)
        path3.plot("r", show=True)
    else:
        print("'-p' option not passed. Nothing will be displayed. Add '-h' for help.")


if __name__ == "__main__":
    main()
