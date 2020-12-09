# WA Simulator
from wa_simulator.simulation.system import WASystem

# Chrono specific imports
import pychrono as chrono

class WAChronoSystem(WASystem):
	def __init__(self, step_size, render_step_size=2e-2, contact_method='NSC'):
		super().__init__(step_size, render_step_size)

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

	def Advance(self):
		self.step_number += 1
		self.system.DoStepDynamics(self.step_size)

	def GetSimTime(self):
		self.time = self.system.GetChTime()
		return self.time

	def GetSystem(self):
		return self.system