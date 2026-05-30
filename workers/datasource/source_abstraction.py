from abc import ABC, abstractmethod
from enum import Enum


class SourceState(Enum):
    DISCONNECTED = 0
    READY = 1
    STREAMING = 2
    ERROR = 3


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
    def is_streaming(self):
        pass