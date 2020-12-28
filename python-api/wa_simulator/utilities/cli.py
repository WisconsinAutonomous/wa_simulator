import argparse

class WAArgumentParser(argparse.ArgumentParser):
	def __init__(self, use_defaults=True, description=('Wisconsin Autonomous Simulator')):
		super().__init__(description=description)

		if use_defaults:
			self.add_default_arguments()
	
	def add_default_arguments(self):
		self.add_argument('-s', '--sim_step_size', type=float, help='Simulation Step Size', default=3e-3, dest='step_size')

		# Visualization
		self.add_argument('-rs', '--render_step_size', type=float, help='Render Update Rate [Hz]', default=1 / 50.)
		vis_group = self.add_mutually_exclusive_group()
		vis_group.add_argument('-iv', '--irrlicht', action='store_true', help='Use Irrlicht to Visualize', default=False)
		vis_group.add_argument('-mv', '--matplotlib', action='store_true', help='Use Matplotlib to Visualize', default=False)

		self.add_argument('-r', '--record', action='store_true', help='Record Simple State Data', default=False)
		