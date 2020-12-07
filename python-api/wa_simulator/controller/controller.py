from abc import ABC, abstractmethod # Abstract Base Class

# -------------
# WA Controller
# -------------

class WAController(ABC):
	@abstractmethod
	def Advance(self, step):
		pass

	@abstractmethod
	def Synchronize(self, time):
		pass

	@abstractmethod
	def GetInputs(self):
		pass