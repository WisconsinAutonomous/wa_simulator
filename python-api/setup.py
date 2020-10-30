"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from pathlib import Path

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    here = Path(__file__).parent.resolve()
    return (here / fname).read_text(encoding='utf-8')

setup(
    name = "wa_chrono_sim",
    version = "0.0.1",
    author = "Aaron Young",

    license = "BSD",
    description = ("Simulation tool for prototyping autonomous vehicle related algorithms. Wrapper of the PyChrono simulator."),
    long_description=read('README.md'),
    long_description_content_type='text/markdown',  # Optional (see note above)

    packages=find_packages(),

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Prototyping Tools",
        "License :: OSI Approved :: BSD License",
        'Programming Language :: Python :: 3',
    ],
    keywords='simulation, autonomous vehicles, robotics'

    python_requires='>=3.0, <4',
    install_requires=[
        'matplotlib',
        'numpy',
        'scipy',
    ]

    project_urls={  # Optional
        'Source': 'https://github.com/WisconsinAutonomous/wa_chrono_sim/',
        'Bug Reports': 'https://github.com/WisconsinAutonomous/wa_chrono_sim/issues',
        'Our Team!': 'https://wisconsinautonomous.org',
    },
)