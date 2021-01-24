# Windows Installation Guide

## Conda environment

Anaconda is a really powerful packaging environment available on both Unix and Windows systems. In this guide, you will download an `environment.yml` file which describes a `conda` environment and then create an env from those instructions given in the YaML file.

### Download the environment file

First, let's download the environment file.

In the Command Prompt, you can run the following:
```
curl.exe -o environment.yml https://raw.githubusercontent.com/WisconsinAutonomous/wa_simulator/master/environment.yml
```

In PowerShell, you can run the following:
```
iwr -outf environment.yml https://raw.githubusercontent.com/WisconsinAutonomous/wa_simulator/master/environment.yml
```

### Create the conda environment

Now, let's actually create the environment. _This requires Anaconda to be installed_.

```
conda env create --name=wa -f=environment.yml
```

This will create an environment with the name `wa`, but feel free to change it to anything you'd like.