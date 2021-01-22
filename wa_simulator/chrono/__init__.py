"""
Requires the `PyChrono <https://projectchrono.org/pychrono/>`_ library.
"""

from .._import import _import, _get_files
from .. import *

try:
    # Try to import chrono
    # Will through exception if failed
    import pychrono as chrono
    import pychrono.vehicle as veh
    import pathlib
except Exception as e:
    raise e

# Set the chrono data directory to in-repo data directory
CHRONO_DATA_DIRECTORY = str(pathlib.Path(DATA_DIRECTORY) / "chrono" / " ")[:-1]
CHRONO_VEH_DATA_DIRECTORY = str(
    pathlib.Path(DATA_DIRECTORY) / "chrono" / "vehicle" / " "
)[:-1]

chrono.SetChronoDataPath(CHRONO_DATA_DIRECTORY)
veh.SetDataPath(CHRONO_VEH_DATA_DIRECTORY)


for d in _get_files(__file__):
    _import(d, globals())

del pathlib, _import, _get_files
