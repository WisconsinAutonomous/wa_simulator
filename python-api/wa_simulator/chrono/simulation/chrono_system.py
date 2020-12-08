# WA Simulator
from wa_simulator.simulation.system import WASystem

# Chrono specific imports
import pychrono as chrono

class WAChronoSystem(WASystem):
	def __init__(self, step_size, render_step_size=2e-2, contact_method='NSC'):
		if not isinstance(contact_method, str):
			raise TypeError("Contact method must be of type str")

		if contact_method == 'NSC':
			system = chrono.ChSystemNSC()
		elif contact_method == 'SMC':
			system = chrono.ChSystemSMC()
		system.Set_G_acc(chrono.ChVectorD(0, 0, -9.81))
		system.SetSolverType(chrono.ChSolver.Type_BARZILAIBORWEIN)
		system.SetSolverMaxIterations(150)
		system.SetMaxPenetrationRecoverySpeed(4.0)
		self.system = system

		self.step_number = 0
		self.step_size = step_size
		self.render_step_size = render_step_size

	def Advance(self, step):
		self.step_number += 1
		self.system.DoStepDynamics(step)

	def GetSimTime(self):
		return self.system.GetChTime()

	def GetSystem(self):
		return self.system
	
	def GetStepSize(self):
		return self.step_size

	def GetRenderStepSize(self):
		return self.render_step_size

	def GetStepNumber(self):
		return self.step_number