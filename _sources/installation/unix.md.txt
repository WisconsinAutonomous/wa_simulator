# Unix Installation Guide

## Summary

```shell
# Recommended!!
# To install wa_simulator in an anaconda environment (Linux systems must install anaconda externally)
bash -c "$(curl -fsSL https://raw.githubusercontent.com/WisconsinAutonomous/wa_simulator/master/scripts/config_conda_env.sh)"

# OR

# Not Recommended!!
# To install the wa_simuator separately from Chrono
pip install wa_simulator
```

## Description

The best way to use the `wa_simulator` is within an [Anaconda](https://anaconda.org/) environment. Anaconda environments will isolate package installation from the rest of your computer, minimizing configuration problems and/or conflicting packages.

PyChrono has also released as an [anaconda package](https://anaconda.org/projectchrono/pychrono). The installation script described below will also install this package automatically.

The recommended approach to installing `wa_simulator` on Unix systems (Linux and MacOS) is through the shell script available on the `wa_simulator` github. To install the package via this script, run the following command.

> Note: As mentioned above, this script will utilize Anaconda. On MacOS systems, this will be installed automatically through the Homebrew package manager. On Linux systems, please [install anaconda separately](https://docs.anaconda.com/anaconda/install/linux/).

```shell
bash -c "$(curl -fsSL https://raw.githubusercontent.com/WisconsinAutonomous/wa_simulator/master/scripts/config_conda_env.sh)"
```

For _most_ use cases for this simulator, a conda package installation. For those who want to aid in development of the repository, further instructions for how to do that will be created in the future.

### Without Chrono

`wa_simulator` is also available on [PyPI](https://pypi.org/project/wa-simulator/), so it also can be installed through `pip`. PyChrono requires non-python libraries to function, so it can not be installed via `pip`. Therefore, this installation of `wa_simulator` will not bring in PyChrono. You may build PyChrono from source or install it separately, if desired. _It is **highly** recommended to install this in a conda or virtualenv to isolate the installation_.
```shell
pip install wa_simulator
```
