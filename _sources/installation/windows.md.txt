# Windows Installation Guide

## Pip - Without Chrono

If you'd like to install `wa_simulator` _without_ Chrono, run the following command in PowerShell, Command Prompt, or Anaconda Prompt:

```shell
# To install the wa_simulator separately from Chrono
pip install wa_simulator
```

You may want to use [Python virtual environment](https://docs.python.org/3/tutorial/venv.html) or [Anaconda](https://anaconda.org) in order to isolate your development environment.

## Conda Environment - With Chrono

Anaconda is a really powerful packaging environment available on both Unix and Windows systems. In this guide, you will download an `environment.yml` file which describes a `conda` environment and then create an env from those instructions given in the YaML file.

If you'd like to install `wa_simulator` _with_ Chrono, run the following commands in PowerShell, Command Prompt, or Anaconda Prompt.

This will create an environment with the name `wa`, but feel free to change it to anything you'd like.

```{note}
[Anaconda](https://anaconda.org/) must be installed for you to do this.
```

#### Command Prompt

```shell
curl.exe -o environment.yml https://raw.githubusercontent.com/WisconsinAutonomous/wa_simulator/master/environment.yml
conda env create --name=wa -f=environment.yml
```

#### PowerShell

```shell
iwr -outf environment.yml https://raw.githubusercontent.com/WisconsinAutonomous/wa_simulator/master/environment.yml
conda env create --name=wa -f=environment.yml
```

