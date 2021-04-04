# Simple track demo
# Meant to demonstrate the WA Simulator API
# -----------------------------------------------------------------

# Import the simulator
import wa_simulator as wa
import matplotlib.pyplot as plt

# Command line arguments
parser = wa.WAArgumentParser(use_sim_defaults=False)
parser.add_argument("-p", "--plot", action="store_true", help="Plot the tracks", default=False)
args = parser.parse_args()


def main():
    # Load data points from a csv file
    filename = wa.get_wa_data_file("paths/sample_medium_loop.csv")
    points = wa.load_waypoints_from_csv(filename, delimiter=",") * 2

    # Create the path
    path = wa.WASplinePath(points, num_points=1000, is_closed=True)

    # Create the track with a constant width
    track1 = wa.create_constant_width_track(path, width=6)

    # Create another track from a json file
    filename = wa.get_wa_data_file("tracks/sample_medium_loop.json")
    track2 = wa.create_track_from_json(filename)

    # Check if points are within the boundary
    p1 = wa.WAVector([0, 0, 0])
    p2 = wa.WAVector([25, 25, 0])

    p1_is_inside = track2.inside_boundaries(p1)
    print(f"p1 is {'' if p1_is_inside else 'not '}inside the track boundaries")

    p2_is_inside = track2.inside_boundaries(p2)
    print(f"p2 is {'' if p2_is_inside else 'not '}inside the track boundaries")

    # Plot, if desired
    if args.plot:
        track1.plot(center_args={'color': 'r'}, left_args={'color': 'k'}, right_args={'color': 'k'}, show=False)

        plt.plot(p1.x, p1.y, 'og' if p1_is_inside else 'or')
        plt.plot(p2.x, p2.y, 'og' if p2_is_inside else 'or')
        track2.plot(center_args={'linestyle': '--'}, left_args={'linestyle': ':'}, right_args={'linestyle': '-.'})
    else:
        print("\n'-p' option not passed. Nothing will be displayed. Add '-h' for help.")


if __name__ == "__main__":
    main()
