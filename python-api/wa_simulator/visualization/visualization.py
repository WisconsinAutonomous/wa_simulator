from abc import ABC, abstractmethod # Abstract Base Class

# ----------------
# WA Visualization
# ----------------

class WAVisualization(ABC):
	@abstractmethod
	def Advance(self, step):
		pass

	@abstractmethod
	def Synchronize(self, time, driver_inputs):
		pass