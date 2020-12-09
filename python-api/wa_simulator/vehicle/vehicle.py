from abc import ABC, abstractmethod # Abstract Base Class

# ----------
# WA Vehicle
# ----------

class WAVehicle(ABC):
	@abstractmethod
	def Advance(self, step):
		pass

	@abstractmethod
	def Synchronize(self, time, driver_inputs):
		pass
	
	@abstractmethod
	def GetSimpleState(self):
		pass