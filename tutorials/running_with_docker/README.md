# Running Simulations using Docker

In this tutorial, we will learn how to run `wa_simulator` simulations using Docker.

## Prerequisites

- You have installed `wa_simulator` ([resources for that](https://wisconsinautonomous.github.io/wa_simulator/installation/index.html))
- You have installed `wa_cli` ([resources for that](https://wisconsinautonomous.github.io/wa_cli/installation/index.html))
- You have installed Docker ([resource for that](https://docs.docker.com/get-docker/))

## Background

We'll first give some background and motivation to using Docker with simulations.

To begin, Docker is a tool for virtualizing applications from a main operating system. What this means is that you can run full OS containers within a host OS. The primary purpose behind Docker, and similar tools, is to isolate development environments and to consistently deploy applications across computers. Docker is typically used on servers (think AWS or Azure) to isolate users and to deploy websites and web apps. Docker simply provides the ability to run these isolated containers, it is the users job to create the content that goes inside the containers. For more information on Docker, plesae see their [official website](https://www.docker.com/).

For simulations, containers can be a valuable tool for creating consistent development environments for users with different operating systems or different use cases. For example, a Docker container can be generated that has the entire simulation platform already installed; then, the user can simply run their simulation script in the container without the need to install any dependencies.

## Setup

Beyond installing the packages in [Prerequisites](#prerequisites), there is not much setup that is necessary. The `wa_cli` package provides tools for easily spinning up containers and running simulations within Docker.

## Initializing the Network

To help facilitate complicated scenarios, it is common practice to utilize multiple containers. Think, for instance, with multiple containers, you can have multiple, independent systems that can be interchanged easily. Then, each isolated container communicates with the others in some capacity. This is what we will do here, where we have one container for the simulation, then other containers with other features: for example, `novnc` for visualizing gui apps, `ros` for running control logic, etc.

The way Docker allows containers to work together is through a mechanism called networks. Please refer to the [official documentation](https://docs.docker.com/network/) for a full overview of networks; in summary, they are basically a way to communicate between containers. Each container in your application would connect to the network, and then communicate to each other to facilitate complicated systems.

The first step is then to create a network for all of our containers to communicate on. The `wa_cli` package provides a command to do this. To create a network with all of the default values and with the name `wa`, run the following command:

```bash
wa docker network
```

To learn more about this command, [see the `wa_cli` documentation](https://wisconsinautonomous.github.io/wa_cli/usage.html#docker-network).

```{note}
All subsequent commands will actually create a network if one has not been created; therefore, running this command explicitly is somewhat redundant.
```

## Running the Simulator

To run the simulator in a docker container, the `wa_cli` package provides a command so you don't need to understand the inner workings of Docker. The command has an entrypoint at `wa docker run`. In essence, it is analogous to `docker run` ([documentation](https://docs.docker.com/engine/reference/run/)), except it has useful helper methods for WA members.

To run the [demo\_bicycle\_simple.py](https://github.com/WisconsinAutonomous/wa_simulator/blob/develop/demos/simple/demo_bicycle_simple.py) in a docker container, you can run the following command, in the `wa_simulator` [repository](https://github.com/wisconsinautonomous/wa_simulator):

```bash
$ cd demos/simple/
$ wa docker run --data ../data/ --wasim-without-novnc demo_bicycle_simple.py -mv --end_time 1 # set 'end_time' so it will time out
Verbosity has been set to WARNING
Done.
```

The `--data` part tells docker to copy the data folder to the container so that it can successfully create the vehicle. Further, `--wasim` tells `wa docker run` to use the default values for `wa_simulator` scripts.

### Displaying Visualizers

The aforementioned command, however, isn't that useful since you can't actually see anything. Using [networks](#initializing-the-network) and a tool called `novnc` (see [this](https://novnc.com/info.html) for more information), you can actually display `wa_simulator` visualizations in your browser. 

The `wa_cli` package also provides a useful command to initialize this. A container running `novnc` will be created that communicates with the `wa_simulator` container via a network. To create this container, run the following command:

```bash
wa docker novnc
```

Then rerun the `demo_bicycle_simple.py` script with novnc enabled:

```bash
$ wa docker run --data ../data/ --wasim demo_bicycle_simple.py -mv
```

You should not navigate to [http://localhost:8080/vnc\_auto.html](http://localhost:8080/vnc_auto.html) and you should see a matplotlib window. You should also be able to use the arrow keys to control the vehicle. Note: the framerate may be relatively low.

```{note}
`novnc` should also work with other applications and is not specific to `wa_simulator` visualizations.
```

### Running Containers with Additional Imports

The `wa_cli` package has a very useful command in `wa docker run`, as described [earlier](#running-the-simulator). For some applications, such as the demo `demo_bicycle_pid.py` [here](https://github.com/WisconsinAutonomous/wa_simulator/blob/develop/demos/path_follower/demo_bicycle_pid.py), which utilizes an external file `pid_controller.py`. If you were to just run the container as we did earlier, you would get an import error. You need to add an additionial data file pointing to the `pid_controller.py` file so that docker knows to copy it to the container. As example, to do this, run the following command:

```bash
$ cd demos/path_follower/
$ wa docker run --data ../data/ --data pid_controller.py --wasim demo_bicycle_simple.py
```

If you then have `novnc` running and you go to [http://localhost:8080/vnc\_auto.html](http://localhost:8080/vnc_auto.html), you should see the matplotlib visualization running.

### Running with ROS

Another common use case for the Wisconsin Autonomous team is to use `wa_simulator` with our ROS-based control stacks. For more information on ROS and our use of it, please see [this guide](https://wisconsinautonomous.github.io/posts/ros-overview/).

A demo has been provided which outlines the use of the `WABridge` component in the `wa_simulator` API, which allows communication with external entities of simulation data. The demo can be found [here](https://github.com/WisconsinAutonomous/wa_simulator/tree/develop/demos/bridge). This example can be run completely outside of docker, where the server connects directly to the client. In this tutorial, however, we would like to communicate with a ROS stack located in a docker container. To do this, spin up the server in a docker container with the following command:

```bash
$ cd demos/demo_bridge_server.py
$ wa docker run --wasim --data "../data" --data "pid_controller.py" demo_bridge_server.py
```

The server will then block until a client is found. The client in this case should be the `wa_simulator_ros_bridge` [found here](https://github.com/WisconsinAutonomous/wa_simulator_ros_bridge). Please refer to the [ROS Overview Wiki page](https://wisconsinautonomous.github.io/posts/ros-overview/#using-simulations) for information on how to start the client.

## Using a Development Image

In the previous examples, you were using the `wiscauto/wa_simulator:latest` image, by default. This is a public release; however, you may need to develop `wa_simulator` and use a local build of the image. Further, you could techincally use a completely different image and run any generic python file, though I'd just recommend sticking to `docker run` for that.

### Build a Development Image

To use a development image, you first need to build one. To faciliate easily building the image, `docker-compose` is used. This is a separate, but related, application from `docker`, so you will need to install that separately. Please refer to the [official documentation](https://docs.docker.com/compose/install/) for instructions on how to install that.

To build a development image based on any changes you've made to your local copy of the `wa_simulator` repo, run the following command **from anywhere _within_ the repository**:

```bash
$ docker-compose build wasim-dev
```

The first time you run this command, it may take a while.

### Running a Development Image

To now run a `wa_simulator` script with the develop image, you can run something similar to the following:

```bash
$ cd demos/simple/
$ wa docker run --image wiscauto/wa_simulator:develop --data ../data/ --wasim demo_bicycle_simple.py -mv
```

## Next Steps

You should now have a good understanding of how to use Docker with `wa_simulator`. Happy coding!

## Support

Contact [Wisconsin Autonomous](mailto:wisconsinautonomous@studentorg.wisc.edu) for any questions or concerns regarding the contents of this repository.

## See Also

Follow us on [Facebook](https://www.facebook.com/wisconsinautonomous/), [Instagram](https://www.instagram.com/wisconsinautonomous/), and [LinkedIn](https://www.linkedin.com/company/wisconsin-autonomous/about/)!

<br>

<div>
	<img src="https://github.com/WisconsinAutonomous/wa-resources/blob/master/Images/WA.png?raw=true" alt="Wisconsin Autonomous Logo" class="readme-img" height="100px">  
	<img src="https://github.com/WisconsinAutonomous/wa-resources/blob/master/Images/UWCrest.png?raw=true" alt="University of Wisconsin - Madison Crest" class="readme-img" height="100px" align="right">
</div>
