# WA Vehicle Simulator - 0.0.1


The WA Simulator is a powerful, multi-platform, lightweight and *user-friendly* simulation platform for testing algorithms intended for autonomous robot or vehicle applications.
This project is under active development by [Wisconsin Autonomous](https://wisconsinautonomous.org/), a student organization at the University of Wisconsin - Madison.

_Last Update_: Saturday, January 9th, 2021

## Introduction

This simulator is essentially a wrapper of the high fidelity, physics based simulation engine [ProjectChrono](http://www.projectchrono.org/) and it's python wrapped bindings [PyChrono](http://www.projectchrono.org/pychrono/). ProjectChrono has separate _modules_ which can be optionally built and can enhance certain the use of Chrono for our applications. At the time of writing, modules that are intended to be used with this wrapper are the following: Chrono::Engine (_required_), Chrono::Vehicle (_required_), Chrono::Irrlicht (_optional_), PyChrono (_optional_), Chrono::Sensor (_optional_) and SynChrono (_optional_).

Brief explanation of the aforementioned modules:

  - [Chrono::Engine](http://api.projectchrono.org/manual_root.html): This is the baseline module for Chrono. It provides multi-purpose classes and functions used by all subsequent modules. The underlying physics engine is included in this module.

  - [Chrono::Vehicle](http://api.projectchrono.org/manual_vehicle.html): The vehicle module is built on top of Chrono::Engine and provides a framework for modeling high fidelity wheeled _and_ tracked vehicles. This module is required specifically because it provides the functionality to create custom vehicle models.

  - Chrono::Irrlicht: [Irrlicht](http://irrlicht.sourceforge.net/) is a realtime 3D rendering engine written in C++. It is a very old framework and is likely to be updated by the Chrono developers in the near future. It provides the realtime visualization most common to day-to-day development.

  - [PyChrono](http://api.projectchrono.org/pychrono_introduction.html): PyChrono is the python wrapped bindings of the C++ Chrono project. This allows users to access _most_ Chrono functionality through a python API. This aids in rapid development and deployment of autonomous algorithms and is easy to use.

  - [Chrono::Sensor](http://api.projectchrono.org/manual_sensor.html): The sensor module enables the ability to model and simulate sensors in a Chrono environment. Two types of sensors are available: dynamic and static. Dynamic sensors use the NVIDIA based ray tracing library [OptiX](https://developer.nvidia.com/optix) and allow for simulation of sensors such as cameras or LiDARs. Static sensors do not require ray tracing, e.g. GPS, IMU, etc.

  - SynChrono: SynChrono is a new module aimed to provide multi-agent, distributed simulation for Chrono. Primarily as an addition to the vehicle module, SynChrono is built with either MPI or DDS as the message passing protocol.

As the previous modules describe, there is abundant possibilities to create and test autonomous algorithms. This repository will provide scripts, documentation and wrapped classes aiding in quickly working with Chrono.

## Setup Guide

Detailed installation guides for this repository have been written for Windows and Unix based operating systems (separate MacOS and Linux guides are available). Please follow the guide that is relevant to the operating system you're using.

<!-- Windows: [Setup Guide](https://github.com/WisconsinAutonomous/control_sandbox/blob/master/WindowsSetup.md)\ -->
<!-- Mac: [Setup Guide](https://github.com/WisconsinAutonomous/control_sandbox/blob/master/UnixSetup.md) -->
<!-- Linux: [Setup Guide](https://github.com/WisconsinAutonomous/control_sandbox/blob/master/UnixSetup.md) -->

## Running

`TODO`

## License 
wa_simulator is made available under the BSD-3 License. For more details, see [LICENSE](https://github.com/WisconsinAutonomous/wa_simulator/blob/develop/LICENSE).


## Support

Contact [Aaron Young](aryoung5@wisc.edu) for any questions or concerns regarding the contents of this repository.

## See Also

Stay up to date with our technical info by following our [blog](https://www.wisconsinautonomous.org/blog).

Follow us on [Facebook](https://www.facebook.com/wisconsinautonomous/), [Instagram](https://www.instagram.com/wisconsinautonomous/), and [LinkedIn](https://www.linkedin.com/company/wisconsin-autonomous/about/)!

<br>

<div>
	<img src="https://github.com/WisconsinAutonomous/wa-resources/blob/master/Images/WA.png?raw=true" alt="Wisconsin Autonomous Logo" class="readme-img" height="100px">  
	<img src="https://github.com/WisconsinAutonomous/wa-resources/blob/master/Images/UWCrest.png?raw=true" alt="University of Wisconsin - Madison Crest" class="readme-img" height="100px" align="right">
</div>