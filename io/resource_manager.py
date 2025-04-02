from ..utility.z_base import Singleton

from enum import Enum, auto

class DeserializerType(Enum):
    JSON = auto()
    YAML = auto()
    XML = auto()

class ResourceManager(Singleton):
    def 