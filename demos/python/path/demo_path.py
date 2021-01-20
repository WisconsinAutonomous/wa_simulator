# Simple path demo
# Meant to demonstrate Python API
# PLEASE DON'T CHANGE
# -----------------------------------------------------------------

# Import the simulator
import wa_simulator as wa

# Command line arguments
parser = wa.WAArgumentParser(use_defaults=False)
parser.add_argument(
    "-p",
    "--plot",
    action="store_true",
    help="Plot the paths",
    default=False,
)
args = parser.parse_args()


def main():

    points = [
        [49.8, 132.9],
        [60.3, 129.3],
        [75.6, 129.0],
        [87.9, 131.7],
        [96.9, 129.6],
        [111.0, 120.0],
        [115.2, 110.7],
        [120.6, 96.9],
        [127.8, 88.5],
        [135.9, 77.4],
        [135.9, 65.1],
        [133.2, 51.3],
        [128.4, 43.2],
        [119.7, 36.3],
        [105.0, 35.7],
        [90.0, 36.3],
        [82.5, 46.2],
        [82.5, 63.6],
        [83.4, 82.2],
        [77.1, 93.9],
        [61.2, 88.5],
        [55.5, 73.5],
        [57.9, 54.6],
        [66.6, 45.0],
        [75.9, 36.3],
        [79.2, 25.5],
        [78.0, 13.2],
        [65.1, 6.0],
        [50.7, 6.0],
        [36.6, 11.7],
        [29.1, 21.3],
        [24.0, 36.9],
        [24.0, 56.1],
        [29.1, 70.8],
        [24.9, 77.7],
        [13.5, 77.7],
        [6.3, 81.6],
        [5.7, 92.7],
        [6.3, 107.7],
        [8.7, 118.2],
        [15.3, 122.7],
        [24.3, 125.4],
        [31.2, 126.0],
        [40.8, 129.6],
        [49.8, 132.9],
    ]

    plot = wa.WASplinePath(points, num_points=1000)

    if args.plot:
        plot.plot("k", show=True)


if __name__ == "__main__":
    main()
