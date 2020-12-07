from abc import ABC, abstractmethod # Abstract Base Class

class WATerrain(ABC):
    @abstractmethod
    def Advance(self, step):
        pass

    @abstractmethod
    def Synchronize(self, time):
        pass
