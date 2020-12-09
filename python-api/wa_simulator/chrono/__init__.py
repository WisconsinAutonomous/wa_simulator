from wa_simulator import *

try:
	# Try to import chrono
	# Will through exception if failed
	import pychrono as chrono
	import pychrono.vehicle as veh

	# Set the chrono data directory to in-repo data directory
	CHRONO_DATA_DIRECTORY = DATA_DIRECTORY / 'chrono' / ' '
	CHRONO_VEH_DATA_DIRECTORY = DATA_DIRECTORY / 'chrono' / 'vehicle' / ' '

	CHRONO_DATA_DIRECTORY = str(CHRONO_DATA_DIRECTORY)[:-1]
	CHRONO_VEH_DATA_DIRECTORY = str(CHRONO_VEH_DATA_DIRECTORY)[:-1]

	chrono.SetChronoDataPath(CHRONO_DATA_DIRECTORY)
	veh.SetDataPath(CHRONO_VEH_DATA_DIRECTORY)

	del chrono, veh
except Exception as e:
	print('Couldn\'t import PyChrono.\n')
	raise e

# Import chrono imports
from .vehicle.chrono_vehicle import *
from .environment.chrono_terrain import *
from .environment.chrono_environment import *
from .simulation.chrono_system import *
from .visualization.chrono_irrlicht import *
from .controller.irrlicht_controller import *