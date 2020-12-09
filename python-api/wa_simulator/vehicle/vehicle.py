from abc import ABC, abstractmethod # Abstract Base Class

# WA Simulator
from wa_simulator.utilities.data_loader import GetWADataFile

# ---------------
# Utility Methods
# ---------------
def LoadVisualizationProperties(filename):
    import json

    full_filename = GetWADataFile(filename)

    with open(full_filename) as f:
        j = json.load(f)
        
    if 'Visualization Properties' not in j:
        raise ValueError('Visualization Proprties not found in json.')

    return j['Visualization Properties']

# ----------
# WA Vehicle
# ----------

class WAVehicle(ABC):
	def __init__(self, filename=None):
		if filename is not None:
			self.vis_properties = LoadVisualizationProperties(filename)
			
	@abstractmethod
	def Advance(self, step):
		pass

	@abstractmethod
	def Synchronize(self, time, driver_inputs):
		pass
	
	@abstractmethod
	def GetSimpleState(self):
		pass