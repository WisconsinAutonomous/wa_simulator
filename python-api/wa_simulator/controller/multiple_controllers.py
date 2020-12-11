# WA Simulator
from wa_simulator.controller.controller import WAController

# -----------------------
# WA Multiple Controllers
# -----------------------

class WAMultipleControllers(WAController):
	def __init__(self, controllers):
		self.controllers = controllers

	def Advance(self, step):
		for ctr in self.controllers:
			ctr.Advance(step)

	def Synchronize(self, time):
		for ctr in self.controllers:
			ctr.Synchronize(time)

	def GetInputs(self):
		return ctr[0].GetInputs()