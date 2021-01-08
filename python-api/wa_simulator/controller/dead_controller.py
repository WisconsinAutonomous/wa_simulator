"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

from .controller import WAController  # WA Simulator


class WADeadController(WAController):
    """Simple controller designed to never change the inputs

    Can be used for situations where controlling the vehicle isn't actually necessary
    """

    def Advance(self, step):
        pass

    def Synchronize(self, time):
        pass
