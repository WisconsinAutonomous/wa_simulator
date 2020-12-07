from abc import ABC, abstractmethod # Abstract Base Class

# ----------
# WA Terrain
# ----------

class WATerrain(ABC):
    @abstractmethod
    def Advance(self, step):
        pass

    @abstractmethod
    def Synchronize(self, time):
        pass
