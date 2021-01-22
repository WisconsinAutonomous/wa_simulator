# Contributing

Contributing to the repository is fairly easy. The simulator was developed to be Object Oriented, so the goal was that one could simply inherit any defined class to add their own functionality. There could be bugs or additional features would like to be added, so please see below for instructions how to actually make contributions to the repo.

> Note: If you're contributing to the repository, it can be assumed you know what you're doing. Please be thoughtful in your changes and consult the correct people if you're looking to make changes.

## Setup

It is as simple as cloning and installing a symlinked version of the repository.

### Cloning the repo

Clone the repo as normal:
```bash
git clone https://github.com/WisconsinAutonomous/wa_simulator.git
cd wa_simulator
```

> Make a conda or virtualenv, as that aids in the development process

### Installing a symlinked version for testing

Using a symlink install means we can use the repository as normal, but when we change the source code, our changes will be reflected in any file where `wa_simulator` is imported. This can be done with the following command:
```bash
pip install -e .
```

## Guidelines

A lot of work has gone into making this package scalable and functional. Please consider all of the following guidelines and follow them to ensure the repository will persist for a long time.

### Documentation

Please follow [Google's guidelines for Python Styling](https://google.github.io/styleguide/pyguide.html). These comments are also used to automatically generate the documentation. For Visual Studio Code users, the [Python Docstring Generator](https://github.com/NilsJPWerner/autoDocstring) package may be helpful.

### File Structure

The simulator is structured as follows:
```
wa_simulator
├── docs/				# Contains documentation
├── licenses/ 			# External software licenses
├── scripts/			# Installation scripts
├── tutorials/			# Tutorials for understanding the wa_simulator API
├── wa_simulator/
│   ├── chrono/         # Contains code that requires chrono
│   │	└── ...         # Chrono code     
│   ├── data/         	# Data files that ship with the repo
│   │	└── ...
│   └── ...             # Core code
├── environment.yml
├── LICENSE
└── setup.py
```