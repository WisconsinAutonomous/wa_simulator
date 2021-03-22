"""
Requires the `PyChrono <https://projectchrono.org/pychrono/>`_ library.
"""

from wa_simulator._import import _import, _get_files
from wa_simulator import *

try:
    # Try to import chrono
    # Will through exception if failed
    import pychrono as chrono
    import pychrono.vehicle as veh
except Exception as e:
    raise e

for d in _get_files(__file__):
    _import(d, globals())


del _import, _get_files
