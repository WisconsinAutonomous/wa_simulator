# WA Simulator
from wa_simulator.environment.terrain import WATerrain

# Chrono specific imports
import pychrono as chrono
import pychrono.vehicle as veh

# ---------------
# Utility methods
# ---------------

def ReadTerrainModelFile(filename):
	import json

	full_filename = chrono.GetChronoDataFile(filename)

	with open(full_filename) as f:
		j = json.load(f)

	if 'Terrain' not in j:
		print('\'Terrain\' not present in the passed json file.')
		exit()
	terrain_filename = chrono.GetChronoDataFile(j['Terrain']['Input File'])

	return terrain_filename

# -----------------
# WA Chrono Terrain
# -----------------

class WAChronoTerrain(WATerrain):
	def __init__(self, filename, system):
		# Get the filenames
		terrain_filename = ReadTerrainModelFile(filename)

		# Create the terrain
		self.terrain = veh.RigidTerrain(system.GetSystem(), terrain_filename)
	
	def GetTerrain(self):
		return self.terrain

	def Synchronize(self, time):
		self.terrain.Synchronize(time)

	def Advance(self, step):
		self.terrain.Advance(step)