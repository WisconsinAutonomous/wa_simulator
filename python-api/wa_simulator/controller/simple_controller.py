# WA Simulator
from wa_simulator.controller.controller import WAController

# --------------------
# WA Simple Controller
# --------------------

class WASimpleController(WAController):
	def __init__(self):
		self.steering = 0
		self.throttle = 0
		self.braking = 0

	def Advance(self, step):
		pass

	def Synchronize(self, time):
		pass

	def GetInputs(self):
		return {"steering": self.steering, "throttle": self.throttle, "braking": self.braking}