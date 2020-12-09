# WA Simulator
from wa_simulator.visualization.visualization import WAVisualization

# --------------------------
# WA Multiple Visualizations
# --------------------------

class WAMultipleVisualizations(WAVisualization):
	def __init__(self, visualizations):
		self.visualizations = visualizations

	def Advance(self, step):
		for vis in self.visualizations:
			vis.Advance(step)

	def Synchronize(self, time, driver_inputs):
		for vis in self.visualizations:
			vis.Synchronize(time, driver_inputs)