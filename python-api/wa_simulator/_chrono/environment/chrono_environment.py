# WA Simulator
from wa_simulator.environment.environment import WAEnvironment
from wa_simulator.chrono.environment.chrono_terrain import WAChronoTerrain

# Chrono specific imports
import pychrono as chrono

# ---------------------
# WA Chrono Environment
# ---------------------


class WAChronoEnvironment(WAEnvironment):
    # Global filenames for environment models
    EGP_ENV_MODEL_FILE = "environments/ev_grand_prix.json"
    IAC_ENV_MODEL_FILE = "environments/iac.json"

    def __init__(self, filename, system, terrain=None):
        if terrain is None:
            terrain = WAChronoTerrain(filename, system)

        self.terrain = terrain

    def GetTerrain(self):
        return self.terrain

    def Advance(self, step):
        self.terrain.Advance(step)

    def Synchronize(self, time):
        self.terrain.Synchronize(time)
