# WA Simulator
from wa_simulator.environment.environment import WAEnvironment

class WASimpleEnvironment(WAEnvironment):
	# Global filenames for environment models
	EGP_ENV_MODEL_FILE = 'environments/ev_grand_prix.json'
	IAC_ENV_MODEL_FILE = 'environments/iac.json'

	def __init__(self, filename, system):
		pass

	def Advance(self, step):
		pass

	def Synchronize(self, time):
		pass
