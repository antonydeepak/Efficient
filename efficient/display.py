from abc import ABC
from abc import abstractmethod

class Display(ABC):
    @abstractmethod
    def write(self, message, color):
        raise NotImplementedError('abstract type')

    @abstractmethod
    def clear(self):
        raise NotImplementedError('abstract type')