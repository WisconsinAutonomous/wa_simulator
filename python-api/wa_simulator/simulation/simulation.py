class WASimulation:
	def __init__(self, system, environment, vehicle, visualization, controller):
		self.system = system
		self.environment = environment
		self.vehicle = vehicle
		self.visualization = visualization
		self.controller = controller

	def Record(self, filename):
		with open(filename, 'a+') as f:
			x,y,yaw,v = self.vehicle.GetSimpleState()
			f.write(f'{x},{y},{yaw},{v}')

	def Advance(self, step):
		self.system.Advance()

		self.environment.Advance(step)
		self.vehicle.Advance(step)
		self.visualization.Advance(step)
		self.controller.Advance(step)

	def Synchronize(self, time):
		driver_inputs = self.controller.GetInputs()

		self.controller.Synchronize(time)
		self.vehicle.Synchronize(time, driver_inputs)
		self.environment.Synchronize(time)
		self.visualization.Synchronize(time, driver_inputs)
	
	def Run(self):
		self.step_size = self.system.GetStepSize()
		while True:
			time = self.system.GetSimTime()

			self.Synchronize(time)
			self.Advance(self.step_size)