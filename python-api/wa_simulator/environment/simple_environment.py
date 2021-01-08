"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

from .environment import WAEnvironment  # WA Simulator


class WASimpleEnvironment(WAEnvironment):
    """Simple environment that doesn't have any assets within the world.

    Args:
        filename (str): filename
        sys (WASystem): system

    Attributes:
        EGP_ENV_MODEL_FILE (str): evGrand Prix json file that describes an environment for that comp.
        IAC_ENV_MODEL_FILE (str): Indy Autonomous Challange json file that describes an environment for that comp.
    """

    # Global filenames for environment models
    EGP_ENV_MODEL_FILE = "environments/ev_grand_prix.json"
    IAC_ENV_MODEL_FILE = "environments/iac.json"

    def __init__(self, filename, sys):
        pass

    def Synchronize(self, time):
        """Synchronize the environment with the rest of the world at the specified time

        Doesn't actually do anything.

        Args:
            time (double): the time at which the enviornment should be synchronized to
        """
        pass

    def Advance(self, step):
        """Advance the state of the environment

        Doesn't actually do anything.

        Args:
            step (double): the time step at which the enviornment should be advanced
        """
        pass
