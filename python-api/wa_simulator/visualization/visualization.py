# =============================================================================
# Wisconsin Autonomous - https://www.wisconsinautonomous.org
#
# Copyright (c) 2021 wisconsinautonomous.org
# All right reserved.
#
# Use of this source code is governed by a BSD-style license that can be found
# in the LICENSE file at the top level of the repo
#
# =============================================================================
#
# Base class for visualization implementations for the simulator
#
# All visualization classes should inherit from this class to ensure everything
# functions correctly
#
# =============================================================================

from abc import ABC, abstractmethod # Abstract Base Class

# ----------------
# WA Visualization
# ----------------

class WAVisualization(ABC):
	"""
	author: 
	"""
	@abstractmethod
	def Advance(self, step):
		pass

	@abstractmethod
	def Synchronize(self, time, driver_inputs):
		pass

	@abstractmethod
	def IsOk(self):
		pass