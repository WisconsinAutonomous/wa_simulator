import wa_simulator as wa
import matplotlib.pyplot as plt

def main():

    # Load track data points from a csv file
    wa.set_wa_data_directory('../../data/')
    filename = wa.get_wa_data_file("paths/sample_medium_loop.csv")
    waypoints = wa.load_waypoints_from_csv(filename, delimiter=",")

    # Create the path
    path = wa.WASplinePath(waypoints, num_points=1000, is_closed=True)
    # Create the track with a constant width
    track = wa.create_constant_width_track(path, width=10)
    
    path = getCenterlinePath(track)

    # Plot track boundaries with our new path
    plt.axis('equal')
    path.plot("red", show=False)
    track.left.plot("black", show=False)
    track.right.plot("black")

def getCenterlinePath(track):

    midpoints = [] # list of midpoints along track

    for point in track.center.get_points():

        # using calc_closest_point(), we can ensure the path is parallel to the track boundaries
        left_point = track.left.calc_closest_point(point)
        right_point = track.right.calc_closest_point(point)

        midpoint_x = (right_point[0] + left_point[0]) / 2
        midpoint_y = (right_point[1] + left_point[1]) / 2

        midpoints.append([midpoint_x, midpoint_y, 0])

    path = wa.WASplinePath(midpoints, num_points=1000)
    
    return path

# Will call the main function when 'python custom_controller_demo.py' is run
if __name__ == "__main__":
    main()