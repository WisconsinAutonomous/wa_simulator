"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from pathlib import Path
import os
import re

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    here = Path(__file__).parent.resolve()
    return (here / fname).read_text(encoding="utf-8")


def get_package_data(directory, rm='wa_simulator/'):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join(path.split(rm)[1], filename))
    return paths


# Get the version (borrowed from SQLAlchemy)
def get_version():
    with open(os.path.join(os.path.dirname(__file__), "wa_simulator", "_version.py")) as fp:
        return (
            re.compile(
                r""".*__version__ = ["'](.*?)['"]""", re.S).match(fp.read()).group(1)
        )


setup(
    name="wa_simulator",
    version=get_version(),
    author="Wisconsin Autonomous",
    author_email="wisconsinautonomous@studentorg.wisc.edu",
    license="BSD3",
    description=(
        "Simulation tool for prototyping autonomous vehicle related algorithms. Wrapper of the PyChrono simulator."
    ),
    long_description=read("README.md"),
    long_description_content_type="text/markdown",  # Optional (see note above)
    packages=find_packages(),
    package_data={"wa_simulator": get_package_data("wa_simulator/data")},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
    ],
    keywords="simulation, autonomous vehicles, robotics",
    python_requires=">=3.0",
    install_requires=[
        "matplotlib>=3.3.2",
        "numpy>=1.19.3",
    ],
    project_urls={  # Optional
        "Homepage": "https://github.com/WisconsinAutonomous/wa_simulator/",
        "Documentation": "https://WisconsinAutononomous.github.io/wa_simulator",
        "Bug Reports": "https://github.com/WisconsinAutonomous/wa_simulator/issues",
        "Source Code": "https://github.com/WisconsinAutonomous/wa_simulator/",
        "Our Team!": "https://wisconsinautonomous.org",
    },
)
