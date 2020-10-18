# Windows Setup Guide

In this guide, the installation and setup processes for this repository will be described. This is specifically for the Windows operating system. If you instead have a Unix based operating system, like MacOS or Linux, [follow this guide instead](https://github.com/WisconsinAutonomous/control_sandbox/blob/master/UnixSetup.md).

## Clone repo

First, clone the repository on your local machine. Please ensure you pull the submodules, as well.

Please create a folder that you would like this repository to be stored in. For all commands, make sure you are in the correct place.

If you are using a [Git BASH](https://gitforwindows.org/), run this command in the command window:
```
git clone --recursive https://github.com/WisconsinAutonomous/control_sandbox.git && cd control_sandbox
```

Note: If the repo was cloned without submodules pulled, run this command:
```
git submodule update --init --recursive
```

If you are using some git app, such as [SourceTree](https://www.sourcetreeapp.com/), please clone this repo and its respective submodules with your relevant commands.

## Installation of PyChrono

This simulator requires the [ProjectChrono](http://www.projectchrono.org/) physics simulation engine. However, with the demos currently implemented, only the python wrapper is used. Therefore, in this guide, the python wrapper version will be installed, known as [PyChrono](http://www.projectchrono.org/pychrono/). This subsquent section will install PyChrono using [Anaconda](https://docs.anaconda.com/anaconda). If you would instead like to build from soure (_not recommended unless you know what you're doing_), please refer to this [resource](http://api.projectchrono.org/module_python_installation.html) and skip to [here](#installation-of-the-controls-simulator).

### For Windows Users

In the remainder of this tutorial, you will need to use the Windows Command Prompt. Please launch this application. All subsequent commands should be run in the Command Prompt.

For Windows users, it is recommended to install PyChrono through Anaconda. To install Anaconda, please refer to this [link](https://docs.anaconda.com/anaconda/install/windows/).

Once installed, activate an environment you would like to install PyChrono to. It is recommended to make a new environment and install everything here. [A good resource for help with that.](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

Create a conda environment with python3.7
```
conda create -n env python=3.7 && conda activate env
```

Now, in your conda environment, run the following command:
```
conda install -c projectchrono/label/develop pychrono
```
This will install the news develop version of PyChrono. This newer version is required for the demos in this repo.

Note: For some, an error occurred saying the package could not be found. If this happens to you, you may need to add the channel `conda-forge` to the install path for conda. To do this, run the following command:
```
conda config --add channels conda-forge
```

It's that easy!

### Verify installation of PyChrono

Verify successful installation with this command:
```
python -c 'import pychrono'
```
If this command runs without error, you're good to go!

If you get an error, that's no fun. Please fill out an [issue](https://github.com/WisconsinAutonomous/control_sandbox/issues/new) with information on your specific error and what system you are running on.

## Installation of the controls simulator

First, lets make sure you are in the right place. Run the following command which will print out your current working directory.
```
cd
```
If the end portion of the output says `/control_sandbox`, then you're good to go. If it doesn't, please use `cd <directory>` to move around your file system. It is assumed that you are currently in the control_sandbox directory for the subsequent commands.

As seen in the control_utilities folder, there are a few utility files created that help describe the path and generate a simulation. This removes the direct need for all users to interact with the simulation engine directly.

In order to link to these files, there are two solutions. The first is recommended, but both work.

#### Add the files to your PYTHONPATH
_[Link as reference](https://helpdeskgeek.com/how-to/create-custom-environment-variables-in-windows/)_
1. First, find the current directory\
    Run `cd` in your command prompt. Copy the output. **_Should end in `\control_sandbox`_**.\
      Ex. `C:\Users\user\control_sandbox\`
2. Open the System Properties dialog, click on Advanced and then Environment Variables
3. Under User variables, click New... and create a variable as described below\
    Variable name: `PYTHONPATH`\
    Variable value: `<paste output from 1>\control_utilities\control_utilities`\
      Ex. Variable value: `C:\Users\user\control_sandbox\control_utilities\control_utilities`

#### Install it to your system _Not recommended_
To use the simulator, you can also install it as a local python module. You must enter the control_utilities directory and run a simple command:
```
cd control_utilities && easy_install .
```
Note: If you get an error, run instead `cd control_utilities && python setup.py install --user --prefix=`.

#### Link the chrono data directory to the project.
**_For users using conda, this should not be required._** If an error is received saying something about `CHRONO_DATA_DIR`, please do the following.

_[Link as reference](https://helpdeskgeek.com/how-to/create-custom-environment-variables-in-windows/)_
1. First, find the current directory\
    Run `cd` in your command prompt. Copy the output. **_Should end in `\control_sandbox`_**.\
      Ex. `C:\Users\user\control_sandbox\`
2. Open the System Properties dialog, click on Advanced and then Environment Variables
3. Under User variables, click New... and create a variable as described below\
    Variable name: `CHRONO_DATA_DIR`\
    Variable value: `<paste output from 1>\chrono\data\`\
      Ex. Variable value: `C:\Users\user\control_sandbox\chrono\data\`

**[You should now be ready to use the demos.](https://github.com/WisconsinAutonomous/control_sandbox/blob/master/README.md)**
