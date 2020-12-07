# ----------------------------------------------------------------------------------------
#
# Load in custom data files from the wa_chrono_sim repo
#
# ----------------------------------------------------------------------------------------

import pathlib

import pychrono as chrono
import pychrono.vehicle as veh

DATA_DIRECTORY = pathlib.Path(__file__).absolute().parent.parent.parent.parent / 'data' / ' '
VEH_DATA_DIRECTORY = pathlib.Path(__file__).absolute().parent.parent.parent.parent / 'data' / 'models' / 'vehicles' / ' '

DATA_DIRECTORY = str(DATA_DIRECTORY)[:-1]
VEH_DATA_DIRECTORY = str(VEH_DATA_DIRECTORY)[:-1]

chrono.SetChronoDataPath(DATA_DIRECTORY)
veh.SetDataPath(VEH_DATA_DIRECTORY)