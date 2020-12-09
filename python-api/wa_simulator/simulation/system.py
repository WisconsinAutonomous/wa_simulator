from abc import ABC, abstractmethod # Abstract Base Class

class WASystem(ABC):
	def __init__(self, step_size, render_step_size=2e-2):
		self.step_number = 0
		self.step_size = step_size
		self.render_step_size = render_step_size

		self.time = 0

	def Advance(self):
		self.time += self.step_size

	def GetSimTime(self):
		return self.time
	
	def GetStepSize(self):
		return self.step_size

	def GetRenderStepSize(self):
		return self.render_step_size

	def GetStepNumber(self):
		return self.step_number

	