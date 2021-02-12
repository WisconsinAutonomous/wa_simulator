import os
import inspect
import importlib


def _not_hidden(f):
    return f[0] != "_" and f[0] !='.'


def _get_files(file_):
    return [
        os.path.splitext(f.name)[0]
        for f in os.scandir(os.path.dirname(file_))
        if f.is_file() and _not_hidden(f.name)
    ]


def _get_dirs(file_, ignore=[]):
    return [
        os.path.splitext(f.name)[0]
        for f in os.scandir(os.path.dirname(file_))
        if f.is_dir() and _not_hidden(f.name) and f.name not in ignore
    ]


def _import(module, gbls, ignore=[]):
    # Get caller info
    filename = inspect.stack()[1].filename
    path = os.path.dirname(os.path.realpath(filename)).split("wa_simulator")[-1]
    path = f"wa_simulator{path.replace(os.path.sep, '.')}" if path else "wa_simulator"

    # get a handle on the module
    mdl = importlib.import_module(f"{path}.{module}")

    # is there an __all__?  if so respect it
    if "__all__" in mdl.__dict__:
        names = mdl.__dict__["__all__"]
    else:
        # otherwise we import all names that don't begin with _
        names = [x for x in mdl.__dict__ if not x.startswith("_")]

    # now drag them in
    gbls.update({k: getattr(mdl, k) for k in names})
