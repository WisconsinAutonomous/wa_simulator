# Creating a Centerline Path Planner

In this tutorial, we will use WA Simulator components to generate a centerline path along a track.

## Prerequisites

- Basic understanding of the command line
- Basic understanding of Python
- You have `wa_simulator` installed ([resources for that](https://wisconsinautonomous.github.io/wa_simulator/installation/index.html))
- You have cloned the `wa_internal` repository

> Note: This tutorial assumes you have installed the wa_simulator via Anaconda

## Setup

Since `wa_simulator` is installed via `conda`, creating a path planner is as easy as creating a single file. That is what we'll do in this tutorial.

Please `cd` into a location where you would like to place these files. Create a directory called `centerline_path` with a file called `path_demo.py`. Your file structure should look like this:
```
centerline_path
└── path_demo.py
```

## Set up path_demo.py

To begin, open `path_demo.py` in your favorite editor. I recommend [Atom](https://atom.io/) or [Visual Studio Code](https://code.visualstudio.com/).

We will need to import libraries `wa_simulator` and `matplotlib` as well as set up the main function of demo_path.py.

```python
import wa_simulator as wa
import matplotlib.pyplot as plt

# does nothing for now
def main():
    pass

# Will call the main function when 'python path_demo.py' is run
if __name__ == "__main__":
    main()
```

## Create the Track

Before we start working on our path planner, we need to set up a track to generate a path off of. WA Simulator provides functions which allow us to easily create a track using data from a csv file. 

In this example, we're going to use `sample_medium_loop.csv` which is located in `wa_internal/data/paths`
>Note: You may need to modify the arguments of `wa.set_wa_data_directory()` or `wa.get_wa_data_file()` depending on where the csv file is located relative to `path_demo.py`. In this example, we are running `path_demo.py` in `wa_interal/controls/centerline_path`

```python
def main():
    # Load data points from a csv file
    wa.set_wa_data_directory('../../data/')
    filename = wa.get_wa_data_file("paths/sample_medium_loop.csv")
    waypoints = wa.load_waypoints_from_csv(filename, delimiter=",")

    # Create a path using data points
    path = wa.WASplinePath(waypoints, num_points=1000, is_closed=True)
    
    # Create the track with a constant width
    track = wa.create_constant_width_track(path, width=10)
    
```

`wa.create_constant_width_track()` give us a `WATrack` object which we will be able to use to generate a path. Note that we created this track using `path` as a centerline reference.

## Set up getCenterlinePath() function

We now have a WATrack that we can find the centerline of. To do this, we "travel" along the track and find the points that lie halfway between the left and right boundaries of the track. In other words we find a list of midpoints between the left and right boundaries. 

Define a function called `getCenterlinePath()` which accepts `track` as an argument. Within this function, create an empty list called `midpoints`. We will populate this list as we go along the points on the track.

To "travel" along the track, we use a for loop that iterates through the points on the tracks centerline. 

```python
def getCenterlinePath(track):
    midpoints = [] # list of midpoints along track

    for point in track.center.get_points():
```

> Note: Every `WATrack` object provides center, left, and right `WASplinePath`'s which are useful when planning a path like this. To give a proper introduction to path planning, we will disregard `track.center` and plan our own centerline path using `track.left` and `track.right` 

## Build list of midpoints

To find the midpoints along the track, we will use the midpoint formula:

$(x_{mid}, y_{mid}) = (\frac{x_1 + x_2}{2} , \frac{y_1 + y_2}{2}$)

In our case $(x_1, y_1)$ is a point on the inner (right) boundary, and $(x_2, y_2)$ is a point on the outer (left) boundary. To get these points, we use `WASplinePath`'s `calc_closest_point()` function, which gives us the closest points on the left or right boundaries relative to where we are along the track.

Once we have these points, we can use the midpoint formula to compute the x and y values of the midpoint between the closest points on the left and right boundaries. We then add this midpoint as a list of (x, y, z) values to our `midpoints` list. 

Finally we create a `WASplinePath` using this list of points. This is our centerline path that we will return back to `main()`.

```python
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
```

## Plot Results

Now that we've generated a path. We want to be able to plot it visually to see our results. We'll accomplish this using the `matplotlib` library that we imported earlier. 

> Note: If you want to learn more about Matplotlib and how to use it, Matplotlib's [website](https://matplotlib.org/) has examples, tutorials, documentation, and other helpful resources.

Adding on to our `main()` function. we will call `getCenterlinePath()` and store the returned `WASplinePath` in a variable called `path`

```python
path = getCenterlinePath(track)
```
Now using `WASplinePath`'s `plot()` function. We plot our new `path` together with the tracks left and right boundaries. 
```python
plt.axis('equal') # avoids image being stretched
path.plot("red", show=False)
track.left.plot("black", show=False)
track.right.plot("black")
```

In the end your `main()` function should look something like this
```python
def main():

    # Load track data points from a csv file
    wa.set_wa_data_directory('../data/')
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
```

## Putting it all together

Your `path_demo.py` should look like this:

```python
import wa_simulator as wa
import matplotlib.pyplot as plt


def main():

    # Load track data points from a csv file
    wa.set_wa_data_directory('../data/')
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


# Will call the main function when 'python path_demo.py' is run
if __name__ == "__main__":
    main()
```

To run the demo, run

```
python path_demo.py
```

You can also find the [code in our GitHub repo](https://github.com/WisconsinAutonomous/wa_simulator/blob/master/tutorials/centerline_path/path_demo.py)

A matplotlib window should pop up showing the track boundaries with a red centerline path! 

You should now have a good understanding of how to plan a path globally in `wa_simulator`. Feel free to edit this demo or add your own logic! Happy Coding!

## Extra - Implementing Alpha

We can modify our formula in slightly to "shift" the path towards the left or right side. 

In `getCenterlinePath()`, define a new variable `alpha` and set it to 0.5. After that, modify the `midpoint_x` and `midpoint_y` assignments to look like this:

```
alpha = 0.5

midpoint_x = right_point[0] + alpha * (left_point[0] - right_point[0])
midpoint_y = right_point[1] + alpha * (left_point[1] - right_point[1])
```

The `alpha` variable determines how far from the boundaries the path will lie. It can be set to any value from 0 to 1. A lower value will bring the path closer to the inner (right) boundary. A higher value will bring the path closer to the outer (left) boundary.

Your function should now look like this

```python
def getCenterlinePath(track):

    midpoints = [] # list of midpoints along track

    for point in track.center.get_points():

        # using calc_closest_point(), we can ensure the path is parallel to the track boundaries
        left_point = track.left.calc_closest_point(point)
        right_point = track.right.calc_closest_point(point)

        alpha = 0.5

        midpoint_x = right_point[0] + alpha * (left_point[0] - right_point[0])
        midpoint_y = right_point[1] + alpha * (left_point[1] - right_point[1])

        midpoints.append([midpoint_x, midpoint_y, 0])

    path = wa.WASplinePath(midpoints, num_points=1000)
    
    return path
```
An alpha value of 0.5 means that the path will fall exactly in the middle of the left and right boundaries. Therefore running this code should give you a centerline path. However, if you change `alpha` to different values between 0 and 1 you will see the path shift to one side or another. Try changing `alpha` to 0.2 or 0.8 and run the code to see how it changes.

Some more complex path planning algorithms incorporate an alpha value like this which changes as you go along the path. A formula computes what the alpha value should be at each point along the path, producing a more efficient path.

## Support

Contact [Aaron Young](mailto:aryoung5@wisc.edu) for any questions or concerns regarding the contents of this repository.

## See Also

Follow us on [Facebook](https://www.facebook.com/wisconsinautonomous/), [Instagram](https://www.instagram.com/wisconsinautonomous/), and [LinkedIn](https://www.linkedin.com/company/wisconsin-autonomous/about/)!
