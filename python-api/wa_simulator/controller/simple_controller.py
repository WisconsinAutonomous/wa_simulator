# WA Simulator
from wa_simulator.controller.controller import WAController

# --------------------
# WA Simple Controller
# --------------------

class WASimpleController(WAController):
	def __init__(self):
		pass

	def Advance(self, step):
		pass

	def Synchronize(self, time):
		pass

	def GetInputs(self):
		return {"steering": 0, "throttle": 0, "braking": 0}