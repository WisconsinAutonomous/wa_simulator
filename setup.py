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


def read_requirements(file: str = "requirements.txt"):
    with open(file) as f:
        required = f.read().splitlines()
        return required


def create_version():
    from setuptools_scm.version import get_local_dirty_tag

    def clean_scheme(version):
        return get_local_dirty_tag(version) if version.dirty else '+clean'

    return {'local_scheme': clean_scheme}


setup(
    name="wa_simulator",
    use_scm_version=create_version,
    author="Wisconsin Autonomous",
    author_email="wisconsinautonomous@studentorg.wisc.edu",
    license="BSD3",
    description=(
        "Simulation tool for prototyping autonomous vehicle related algorithms."
    ),
    long_description=read("README.md"),
    long_description_content_type="text/markdown",  # Optional (see note above)
    packages=find_packages(),
    package_data={},
    entry_points={},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
    ],
    keywords="simulation, autonomous vehicles, robotics",
    python_requires=">=3.0",
    install_requires=read_requirements(),  # noqa
    project_urls={  # Optional
        "Homepage": "https://github.com/WisconsinAutonomous/wa_simulator/",
        "Documentation": "https://WisconsinAutononomous.github.io/wa_simulator",
        "Bug Reports": "https://github.com/WisconsinAutonomous/wa_simulator/issues",
        "Source Code": "https://github.com/WisconsinAutonomous/wa_simulator/",
        "Our Team!": "https://wa.wisc.edu",
    },
)
