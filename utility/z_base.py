"""
A collection of classes meant to be inherited from.
"""
from enum import Enum
from typing import Any

class ByteEnum(Enum):
    """Base enum class to use when assigning byte values."""
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[Any]) -> bytes:
        last_value = last_values[-1] if last_values else start
        return bytes([last_value[0] + 1])

class Singleton(object):
    """Base singleton class."""
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Singleton, cls).__new__(cls)
        return cls.instance
