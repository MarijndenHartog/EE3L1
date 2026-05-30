from abc import ABC, abstractmethod
from enum import Enum


from enum import Enum


class SourceState(Enum):

    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2
    READY = 3
    STARTING = 4   
    STREAMING = 5 
    STOPPING = 6   
    ERROR = 7

class DataSource(ABC):

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def cmd_start(self):
        pass

    @abstractmethod
    def cmd_stop(self):
        pass


    @abstractmethod
    def state(self):
        pass