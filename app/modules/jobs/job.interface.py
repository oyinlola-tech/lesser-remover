from abc import ABC, abstractmethod


class JobInterface(ABC):
    @abstractmethod
    def execute(self):
        pass
