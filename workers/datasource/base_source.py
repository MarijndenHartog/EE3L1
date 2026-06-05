from abc import ABC, abstractmethod


class BaseSource(ABC):

    @abstractmethod
    def start_source(self): pass

    @abstractmethod
    def stop_source(self): pass

    @abstractmethod
    def cmd_burst(self, duration_ms, frequency_hz): pass

    @abstractmethod
    def get_state(self): pass