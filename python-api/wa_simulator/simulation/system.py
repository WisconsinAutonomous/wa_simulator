from abc import ABC, abstractmethod # Abstract Base Class

class WASystem(ABC):
	@abstractmethod
	def Advance(self, step):
		pass

	@abstractmethod
	def GetSimTime(self):
		pass

	