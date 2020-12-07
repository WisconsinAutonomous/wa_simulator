from abc import ABC, abstractmethod # Abstract Base Class

class WAVehicle(ABC):
	@abstractmethod
	def Advance(self, step):
		pass