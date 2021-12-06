from wa_simulator._import import _import, _get_files

for d in _get_files(__file__):
    _import(d, globals())

del _import, _get_files
