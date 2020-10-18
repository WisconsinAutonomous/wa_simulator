# Linux Setup Guide

This installation guide was tested on Arch Linux, but should be applicable for _most_ linux distributions.

In this setup guide we will be using command line. Although exact commands will be provided, a basic understanding of the terminal is recommended. _**This setup guide is intended for new programmers/students**_.

_Last Update_: Saturday, October 17th, 2020

## Table of Contents
- [Clone WA Chrono Sim](#clone-repo)
- [Chrono Installation](#installation-of-chrono)
    - [Building Chrono from Source](#building-from-source)
    - [Installing PyChrono with Anaconda](#pychrono-installation-with-anaconda)
- [Support](#support)
- [See Also](#see-also)

## Clone repo

First, clone the repository on your local machine.
```bash
git clone https://github.com/WisconsinAutonomous/wa_chrono_sim.git && cd wa_chrono_sim
```

## Installation of Chrono

This simulator requires the [ProjectChrono](http://www.projectchrono.org/) physics simulation engine. There are two recommended installation choices for Linux operating systems: [building from source](#building-from-source) and/or [PyChrono only through anaconda](#pychrono-installation-with-anaconda).

**For new users, the [anaconda installation](#pychrono-installation-with-anaconda) is recommended.**

### Building from Source

Below are detailed instructions and commands needed to correctly install Chrono from source.

To begin, open up a terminal window if you have not already.

First, make sure you are located in the correct place. Run the following command which will print out your current working directory.
```bash
pwd
```
If the end portion of the output says `.../wa_chrono_sim`, then you're good to go. If it doesn't, please use `cd <directory>` to move around your file system until you're inside the `.../wa_chrono_sim` directory. It will be assumed that you are currently in the `.../wa_chrono_sim` directory for subsequent instructions.

**For the following commands, since Ubuntu is the most common Linux distribution, `apt` packages will be referenced. If you use different package mangers, such as `pacman` or `yay`, please ensure you are installing the correct packages.

1. **Install the required packages**

```bash
sudo apt install cmake python3 libirrlicht-dev libeigen3-dev
```

_Note 1_: Reminder that if you instead are not on Ubuntu, use your respective package manager.

#### _Optional: Install Swig_

_This is only necessary if you intend to install PyChrono._

SWIG is a package that helps wrap C++ code to be used in python (and a lot of other languages). _Other package manager's may have swig available, so please check before proceeding with this process_.

a. Go to the [SWIG download page](http://www.swig.org/download.html) and download the latest swig installation package
b. Unzip the swig zip source code to a local directory
```bash
# Change zip file permission.
chmod 777 swig-3.0.12.tar.gz

# Unzip the tar file.
tar -xzvf swig-3.0.12.tar.gz
```
c. Specify swig install directory
_Replace `$HOME/swig` with wherever you'd like to install SWIG_
```bash
./configure --prefix=$HOME/swig
```
d. Compile and install
```bash
sudo make
sudo make install
```
e. Add to the SWIG_PATH and PATH environment variables
_Again, replace `$HOME/swig` with wherever you chose to install SWIG_
_Also, this assumes bash is your default shell. Replace .bashrc with your correct start-up file_
```bash
echo 'export SWIG_PATH=$HOME/swig' >> ~/.bashrc
echo 'export PATH=$SWIG_PATH:$PATH' >> ~/.bashrc
source ~/.bashrc
```
f. Verify SWIG installation
```bash
swig -version
```

2. **Clone the Wisconsin Autonomous fork of ProjectChrono and create a build directory**

```bash
git clone https://github.com/WisconsinAutonomous/chrono.git && cd chrono && mkdir build && cd build
```

3. **Use cmake and make to build the project**
To build the optional modules, add the following to the cmake command:
    * **Irrlicht**: -DENABLE_MODULE_IRRLICHT:BOOL=ON
    * **PyChrono**: -DENABLE_MODULE_PYTHON:BOOL=ON
    * **Sensor**: -DENABLE_MODULE_SENSOR:BOOL=ON
    * **SynChrono**: -DENABLE_MODULE_SYNCHRONO:BOOL=ON

_NOTE: Replace <cores> with however many CPU cores you would like to build the project with. In general, more cores results in a faster build. To check the number of cores you have, run `lscpu | grep -m 1 'CPU(s):'`. It's recommended to not exceed 2 times that number._

```bash
cmake \
  -DCMAKE_BUILD_TYPE:STRING=Release \
  -DENABLE_MODULE_VEHICLE:BOOL=ON \
  .. \
  && make -j
```

_This will take a little time. Just be patient._


4. **_Optional_: Create a Python environment folder**

*NOTE: This is specifically for PyChrono, which is optional.* Everything can be done outside of a python environment, it just makes things cleaner. For those of you interested, a python environment allows you to install python packages in self contained place. When you exit the env, all of your packages remain, but the rest of your system is unchanged by the installs you made within the env.

a. Create a separate folder to hold the python environment files
```
mkdir PyEnvs && cd PyEnvs
```
b. Create a python environment and activate it
```
python3.8 -m venv pychrono && source pychrono/bin/activate && cd ..
```

5. **_Optional_: Set PYTHONPATH to point to the PyChrono executables**

Within the same build directory, you must add the pychrono files to the PYTHONPATH. Your PYTHONPATH is basically used when you run a python command to search for files you import. Run the following command to set it. _You must be inside your build directory for this specific command to work_.

_Recommended approach._ This will create the correct PYTHONPATH each time you log onto your terminal. Otherwise, you will have to run a command _everytime_.
```
echo "export PYTHONPATH=$PYTHONPATH:$(pwd)/bin" >> ~/.zshrc && source ~/.bashrc
```
_Note: this assumes you are using zsh. Run `echo $0`. If it says `-bash`, replace `~/.zshrc` with `~/.bashrc`._

If you do not want to add it to your `.bashrc` (_not recommended_), just run the following command.
```
export PYTHONPATH=$PYTHONPATH:$(pwd)/bin
```
Note: If you are not in your build directory anymore, please replace `$(pwd)/bin` with the path to chrono/build/bin.

### PyChrono Installation with Anaconda

a. **Install Anaconda and create a Conda environment**

Anaconda is a way to distrubte packages in a simple and easy to manage way. It is used primarily for Python and we will be using it to install PyChrono. _This will not install the C++ interface; see [Building From Source](#building-from-source)._

To install Anaconda, please refer to this [link](https://docs.anaconda.com/anaconda/install/linux/).

Once installed, activate an environment you would like to install PyChrono to. It is recommended to make a new environment and install everything here. [A good resource for help with that.](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

_NOTE: Restart your terminal windows wants the aforementioned installations are completed_

Create a conda environment with python3.8
```
conda create -n pychrono_env python=3.8 && conda activate pychrono_env
```

Now, in your conda environment, run the following command:
```
conda install -c projectchrono/label/develop pychrono
```

_NOTE: For some, an error occurred saying the package could not be found. If this happens to you, you may need to add the channel `conda-forge` to the install path for conda._ To do this, run the following command:
```
conda config --add channels conda-forge
```

b. **Verify installation of PyChrono**

Verify successful installation with this command:
```
python -c 'import pychrono'
```
If this command runs without error, you're good to go!

If you get an error, that's no fun. Please fill out an [issue](https://github.com/WisconsinAutonomous/wa_chrono_sim/issues/new).

# NOT  DONE YET

## Installation of the controls simulator

First, lets make sure you are in the right place. Run the following command which will print out your current working directory.
```
pwd
```
If the end portion of the output says `/control_sandbox`, then you're good to go. If it doesn't, please use `cd <directory>` to move around your file system. It is assumed that you are currently in the `control_sandbox` directory for the subsequent commands.

As seen in the control_utilities folder, there are a few utility files created that help describe the path and generate a simulation. This removes the direct need for all users to interact with the simulation engine directly.

In order to link to these files, there are two solutions. The first is recommended, but both work.

#### _Recommanded_: Add the files to your PYTHONPATH
*This is the recommended approach for installing the simulator.* The environment variable PYTHONPATH is used when you run a python command to find files not in the default folder. As a result, if you add the path of the simulator to that environmental variable, it will work without installing!!

To have it added to your PYTHONPATH, run the following command.
_Recommended_ (will run everytime you open your terminal without you explicitly running the command.)
```
echo "export PYTHONPATH=$PYTHONPATH:$(pwd)/control_utilities" >> ~/.zshrc && source ~/.zshrc
```
Note: this assumes you are using zsh. Run `echo $0`. If it says `-bash`, replace `~/.zshrc` with `~/.bashrc`.

If you do not want to add it to your `.zshrc` (_not recommended_), just run the following command.
```
export PYTHONPATH=$PYTHONPATH:$(pwd)/control_utilities
```

#### Install it to your system _Not recommended_
To use the simulator, it is recommended to install it as a local python module. You must enter the control_utilities directory and run a simple command:
```
cd control_utilities && easy_install .
```
Note: If you get an error, run instead `cd control_utilities && python setup.py install --user --prefix=`.

### Link the chrono data directory to the project.
_Only relevant for users who are **not** using anaconda_.
In order to see the simulation in 3D using irrlicht (a 3D visualizer written in C++), control_sandbox must have access to chrono's data directory. Similar to previously run steps, you must use an environmental variable. Run one of the following commands to successfully link to the data directory. _The first is the recommended solution._

To have it added to your CHRONO_DATA_DIR, run the following command.
_Recommended_ (will run everytime you open your terminal without you explicitly running the command.)
```
echo "export CHRONO_DATA_DIR=$(pwd)/chrono/data/" >> ~/.zshrc && source ~/.zshrc
```
Note: this assumes you are using zsh. Run `echo $0`. If it says `-bash`, replace `~/.zshrc` with `~/.bashrc`.

If you do not want to add it to your `.zshrc` (_not recommended_), just run the following command.
```
export CHRONO_DATA_DIR=$(pwd)/chrono/data/
```

**[You should now be ready to use the demos.](https://github.com/WisconsinAutonomous/control_sandbox/blob/master/README.md)**
