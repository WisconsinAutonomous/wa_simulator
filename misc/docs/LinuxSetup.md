# Linux Setup Guide

This installation guide was tested on Arch Linux, but should be applicable for _most_ linux distributions.

In this setup guide we will be using command line. Although exact commands will be provided, a basic understanding of the terminal is recommended. _**This setup guide is intended for new programmers/students**_.

_Last Update_: Sunday, October 18th, 2020

## Table of Contents
- [Clone WA Chrono Sim](#clone-repo)
- [Chrono Installation](#installation-of-chrono)
    - [Building Chrono from Source](#building-from-source)
    - [Installing PyChrono with Anaconda](#pychrono-installation-with-anaconda)
- [Support](#support)
- [See Also](#see-also)

## Clone repo

First, clone the repository on your local machine. Please ensure you pull the submodules, as well. In this setup guide we will be using command line commands. Please launch a terminal application and run this command:
```
git clone --recursive https://github.com/WisconsinAutonomous/wa_chrono_sim.git && cd wa_chrono_sim
```

Note: If the repo was cloned without submodules pulled, run this command:
```
git submodule update --init --recursive
```

_Note_: You may want to `cd` into the place where you want to clone the respository.

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

**For the following commands, since Ubuntu is the most common Linux distribution, `apt` packages will be referenced. If you use different package mangers, such as `pacman` or `yay`, please ensure you are installing the correct packages.**

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

2. **Create a Build Directory for Chrono**

This repository holds both the utility functions and the WA Chrono fork. Please `cd` into the `wa_chrono_sim` directory. It is assumed that the last directory in `pwd` is `.../wa_chrono_sim`.

```bash
cd chrono && mkdir build && cd build # cd into the chrono directory in preperation to build it
```

3. **Use Cmake and Make to Build the Project**
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


4. **_Optional_: Create a Python Environment Folder**

*NOTE: This is specifically for PyChrono, which is optional.* Everything can be done outside of a python environment, it just makes things cleaner. For those of you interested, a python environment allows you to install python packages in self contained place. When you exit the env, all of your packages remain, but the rest of your system is unchanged by the installs you made within the env.

a. Create a separate folder to hold the python environment files
```
mkdir PyEnvs && cd PyEnvs
```
b. Create a python environment and activate it
```
python3.8 -m venv pychrono && source pychrono/bin/activate && cd ..
```

5. **_Optional_: Set PYTHONPATH to Point to the PyChrono Executables**

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

PyChrono should now be setup. To verify, please see [here](#verify-installation-of-pychrono).

### PyChrono Installation with Anaconda

a. **Install Anaconda and Create a Conda Environment**

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

b. **Verify Installation of PyChrono**

Verify successful installation with this command:
```
python -c 'import pychrono'
```
If this command runs without error, you're good to go!

If you get an error, that's no fun. Please fill out an [issue](https://github.com/WisconsinAutonomous/wa_chrono_sim/issues/new).

## Installation of the WA Chrono Simulator

Let's ensure we are in the correct location by printing out our current working directory with `pwd`. You should be located in the `.../wa_chrono_sim` folder. For subsequent instructions, it is assumed that you are located in that directory.

The WA Chrono simulator provides helpful utilities in both C++ and Python.