# WA Simulator
from wa_simulator.controller.controller import WAController

# Chrono imports
import pychrono.vehicle as veh

class WAIrrlichtController(WAController):
	def __init__(self, visualization, system):
		# Create the interactive driver
		driver = veh.ChIrrGuiDriver(visualization.GetApp())

		render_step_size = system.GetRenderStepSize()

		# Set the time response for steering and throttle keyboard inputs.
		steering_time = 1.0  # time to go from 0 to +1 (or from 0 to -1)
		throttle_time = 1.0  # time to go from 0 to +1
		braking_time = 0.3   # time to go from 0 to +1
		driver.SetSteeringDelta(render_step_size / steering_time)
		driver.SetThrottleDelta(render_step_size / throttle_time)
		driver.SetBrakingDelta(render_step_size / braking_time)

		driver.Initialize()

		self.driver = driver

	def Synchronize(self, time):
		self.driver.Synchronize(time)

	def Advance(self, step):
		self.driver.Advance(step)
	
	def GetInputs(self):
		return self.driver.GetInputs()
	
