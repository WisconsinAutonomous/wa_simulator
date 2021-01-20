"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

import pathlib

# Grab the data folder in the root of this repo
DATA_DIRECTORY = str(pathlib.Path(__file__).absolute().parent / "data")


def get_wa_data_file(filename):
    """Get the absolute path to the file passed

    Args:
            filename (str): file relative to the data folder to get the absolute path for

    Returns:
            str: the absolute path of the file
    """
    return str(pathlib.Path(DATA_DIRECTORY) / filename)


def set_wa_data_directory(path):
    """Set the data path

    Args:
        path (str): relative (or absolute) path where the data is stored
    """
    global DATA_DIRECTORY

    DATA_DIRECTORY = str(pathlib.Path(path).resolve())
