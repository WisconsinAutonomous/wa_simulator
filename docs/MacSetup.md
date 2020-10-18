## Clone repo

First, clone the repository on your local machine. Please ensure you pull the submodules, as well. In this setup guide we will be using command line commands. Please launch a terminal application and run this command:
```
git clone --recursive https://github.com/WisconsinAutonomous/control_sandbox.git && cd control_sandbox
```

Note: If the repo was cloned without submodules pulled, run this command:
```
git submodule update --init --recursive
```

## Installation of PyChrono

This simulator requires the [ProjectChrono](http://www.projectchrono.org/) physics simulation engine. Primarily, it uses the python wrapper version, known as [PyChrono](http://www.projectchrono.org/pychrono/). There are a few installation methods available to you. For Mac users, [you must install from source](#install-from-source). For Linux users, you can either install using [anaconda](#install-using-anaconda) or [install from source](#install-from-source).

### Install using Anaconda

To install Anaconda, please refer to this [link](https://docs.anaconda.com/anaconda/install/windows/).

Once installed, activate an environment you would like to install PyChrono to. It is recommended to make a new environment and install everything here. [A good resource for help with that.](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

### IMPORTANT, RESTART SHELL PRIOR TO CREATING CONDA ENVIRONMENT

Create a conda environment with python3.7
```
conda create -n pychronoenv python=3.7 && conda activate pychronoenv
```

Now, in your conda environment, run the following command:
```
conda install -c projectchrono/label/develop pychrono
```

Note: For some, an error occurred saying the package could not be found. If this happens to you, you may need to add the channel `conda-forge` to the install path for conda. To do this, run the following command:
```
conda config --add channels conda-forge
```

To test your installation, jump down to [here](#verify-installation-of-pychrono).

### Install from Source

**If you are on a Linux distribution, the [anaconda installation](#install-using-anaconda) is recommended.**

_For Mac, the anaconda installation of PyChrono does not work. You get a segmentation fault error when importing the module. As a result, ProjectChrono must be installed from source._

Below are detailed instructions and commands needed to correctly install PyChrono from source. Because Mac users must use this technique (and most users do not have a Linux distribution), the [Homebrew](https://brew.sh/) package manager is used. If you instead have a package manager such as Pacman or apt, replace `brew` with your respective package manager.

First, lets make sure you are in the right place. Run the following command which will print out your current working directory.
```
pwd
```
If the end portion of the output says `/control_sandbox`, then you're good to go. If it doesn't, please use `cd <directory>` to move around your file system. It is assumed that you are currently in the `control_sandbox` directory for the subsequent commands.

Mac prerequisites: [Homebrew](https://brew.sh/) and xcode command line tools (to install, run `xcode-select --install`)

1. **Install the required packages using homebrew**
```
homebrew install cmake python swig irrlicht eigen
```
Note 1: Last reminder that if you instead are on Ubuntu or some other Linux distribution, use your respective package manager.
Note 2: On other Linux distributions, these packages have different names. If a package is not found, please search for the correct package name. _You're using Linux... you can figure it out_.
2. **Create an Environment folder**
*NOTE: Steps 3 and 4 are optional.* Everything can be done outside of a python environment, it just makes it a bit cleaner. For those of you interested, a python environment allows you to install python packages specifically in a self contained place. When you exit the env, all of your packages remain, but the rest of your system is unchanged by the installs you made in the env.
```
mkdir PyEnvs && cd PyEnvs
```
3. **Create a python environment and activate it**
```
python3.7 -m venv pychrono && source pychrono/bin/activate && cd ..
```
4. **Go to the chrono directory that was created when you recursively clone this repo**
```
cd chrono
```
5. **Create a build directory**
```
mkdir build && cd build
```
6. **Use cmake and make to build the project**
```
cmake \
  -DCMAKE_BUILD_TYPE:STRING=Release \
  -DCMAKE_C_COMPILER=$(which clang) \
  -DCMAKE_CXX_COMPILER=$(which clang++) \
  -DENABLE_MODULE_POSTPROCESS:BOOL=ON \
  -DENABLE_MODULE_VEHICLE:BOOL=ON \
  -DENABLE_MODULE_IRRLICHT:BOOL=ON \
  -DENABLE_MODULE_PYTHON:BOOL=ON \
  .. \
  && make -j12
```
This will take a little time. Just be patient.

Note 1: substitute 12 at the end of the command with however many cores you would like to use to build chrono. I typically use all my available cores, i.e. 12.

**_Mac Users:_**
Note 2: For almost all Mac users, you will already have a Python2.7 installed on your system by Apple. As a result, you will need specify the use of Python3 in the last 3 flags of the last command. If you get an error regarding the location of python, please try adding the flags that have to do point to the correct version of python. The command will now look like the following:
```
cmake \
  -DCMAKE_BUILD_TYPE:STRING=Release \
  -DCMAKE_C_COMPILER=$(which clang) \
  -DCMAKE_CXX_COMPILER=$(which clang++) \
  -DENABLE_MODULE_POSTPROCESS:BOOL=ON \
  -DENABLE_MODULE_VEHICLE:BOOL=ON \
  -DENABLE_MODULE_IRRLICHT:BOOL=ON \
  -DENABLE_MODULE_PYTHON:BOOL=ON \
  -DPYTHON_EXECUTABLE:FILEPATH=/usr/local/bin/python3 \
  -DPYTHON_INCLUDE_DIR:FILEPATH=/usr/local/Frameworks/Python.framework/Versions/3.7/include/python3.7m \
  -DPYTHON_LIBRARY:FILEPATH=/usr/local/Frameworks/Python.framework/Versions/3.7/lib/libpython3.7.dylib \
  .. \
  && make -j12
```
These were the flags that were successfully used on a typical mac setup and were found to be successful.

7. **Set PYTHONPATH to point to the pychrono files**

Within the same build directory, you must add the pychrono files to the PYTHONPATH. Your PYTHONPATH is basically used when you run a python command to search for files you import. Run the following command to set it. _You must be inside your build directory for this specific command to work_.

_Recommended approach._ This will create the correct PYTHONPATH each time you log onto your terminal. Otherwise, you will have to run a command _everytime_.
```
echo "export PYTHONPATH=$PYTHONPATH:$(pwd)/bin" >> ~/.zshrc && source ~/.zshrc
```
Note: this assumes you are using zsh. Run `echo $0`. If it says `-bash`, replace `~/.zshrc` with `~/.bashrc`.

If you do not want to add it to your `.zshrc` (_not recommended_), just run the following command.
```
export PYTHONPATH=$PYTHONPATH:$(pwd)/bin
```
Note: If you are not in your build directory anymore, please replace `$(pwd)/bin` with the path to chrono/build/bin.

8. **Return to the control_sandbox folder**
Now run the following command to return to the control_sandbox directory.
```
cd ../..
```

### Verify installation of PyChrono

Verify successful installation with this command:
```
python -c 'import pychrono'
```
If this command runs without error, you're good to go!

Note: If you chose to not use a python evironment, you will most likely have to use `python3 -c 'import pychrono'` instead.

If you get an error, that's no fun. Please fill out an [issue](https://github.com/WisconsinAutonomous/control_sandbox/issues/new).

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
