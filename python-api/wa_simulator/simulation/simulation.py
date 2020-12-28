class WASimulation:
	def __init__(self, system, environment, vehicle, visualization, controller, record_filename=None):
		self.system = system
		self.environment = environment
		self.vehicle = vehicle
		self.visualization = visualization
		self.controller = controller

		self.record_filename = record_filename
		if self.record_filename:
			with open(self.record_filename, 'w') as f:
				pass

		self.step_size = self.system.step_size
			
	def Record(self, filename):
		with open(filename, 'a+') as f:
			x,y,yaw,v = self.vehicle.GetSimpleState()
			f.write(f'{x},{y},{yaw},{v}')

	def Advance(self, step):
		self.system.Advance()

		self.environment.Advance(step)
		self.vehicle.Advance(step)
		self.controller.Advance(step)

		if self.visualization:
			self.visualization.Advance(step)

	def Synchronize(self, time):
		driver_inputs = self.controller.GetInputs()

		self.controller.Synchronize(time)
		self.vehicle.Synchronize(time, driver_inputs)
		self.environment.Synchronize(time)

		if self.visualization:
			self.visualization.Synchronize(time, driver_inputs)
	
	def Run(self):
		while True:
			time = self.system.GetSimTime()

			self.Synchronize(time)
			self.Advance(self.step_size)

			if self.record_filename:
				self.Record(self.record_filename)
	
	def IsOk(self):
		return self.visualization.IsOk() if self.visualization else True