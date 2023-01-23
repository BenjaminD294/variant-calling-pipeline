from abc import ABC, abstractmethod


class AbstractCommand(ABC):
    @abstractmethod
    def invoke(cls, *args):
        pass
