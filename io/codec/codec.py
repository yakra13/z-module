from abc import ABC, abstractmethod
from model import Model

class Codec(ABC):

    @abstractmethod
    def decode(self, content: str|bytes) -> Model:
        pass

    @abstractmethod
    def encode(self, data_model: Model) -> str|bytes:
        pass
