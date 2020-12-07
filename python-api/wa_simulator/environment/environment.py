from abc import ABC, abstractmethod # Abstract Base Class

class WAEnvironment(ABC):
    @abstractmethod
    def Advance(self, step):
        pass

    @abstractmethod
    def Synchronize(self, time):
        pass
