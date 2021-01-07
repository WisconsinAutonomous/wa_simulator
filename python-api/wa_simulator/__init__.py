from ._import import _import, _get_dirs

for d in _get_dirs(__file__):
	_import(d, globals())

del _import, _get_dirs

from time import time as get_wall_time