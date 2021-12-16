from wa_simulator._import import _import, _get_files
from wa_simulator import using_cli

using_cli = True

for d in _get_files(__file__):
    _import(d, globals())

del _import, _get_files
