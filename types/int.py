"""
"""
from typing import Union

class Int8():
    """Class to represent a 8-bit signed integer.
    
    Class Attributes:
        MIN: minimum value -128
        MAX: maximum value  127
        MASK: 8-bit mask    0xFF

    Supports the following operations:
        (+) addition
        (-) subtraction
        (*) multiplication
        (//) floor division
        (%) modulus
        (-) negation
        bit-wise: & | ^ << >>
        comparison: <, >, <=, >=, !=, ==
    """
    MIN  = -128 # -2^7
    MAX  =  127 # 2^7 - 1
    MASK = 0xFF # 8 bits

    def __init__(self, value: int):
        self.value = self._to_int8(value)

    def _to_int8(self, value: int) -> int:
        """Ensure the value is within the 64-bit integer range."""
        if value < self.MIN or value > self.MAX:
            value = (value + (2<<6)) % (2<<7) - (2<<6)
        return value

    def __add__(self, other: Union['Int8', int]) -> 'Int8':
        if isinstance(other, Int8):
            other = other.value
        return Int8(self._to_int8(self.value + other))

    def __sub__(self, other: Union['Int8', int]) -> 'Int8':
        if isinstance(other, Int8):
            other = other.value
        return Int8(self._to_int8(self.value - other))

    def __mul__(self, other: Union['Int8', int]) -> 'Int8':
        if isinstance(other, Int8):
            other = other.value
        return Int8(self._to_int8(self.value * other))

    def __floordiv__(self, other: Union['Int8', int]) -> 'Int8':
        if isinstance(other, Int8):
            other = other.value
        return Int8(self._to_int8(self.value // other))

    def __mod__(self, other: Union['Int8', int]) -> 'Int8':
        if isinstance(other, Int8):
            other = other.value
        return Int8(self._to_int8(self.value % other))

    def __lt__(self, other: Union['Int8', int]) -> bool:
        if isinstance(other, Int8):
            return self.value < other.value
        return self.value < other

    def __gt__(self, other: Union['Int8', int]) -> bool:
        if isinstance(other, Int8):
            return self.value > other.value
        return self.value > other

    def __le__(self, other: Union['Int8', int]) -> bool:
        if isinstance(other, Int8):
            return self.value <= other.value
        return self.value <= other

    def __ge__(self, other: Union['Int8', int]) -> bool:
        if isinstance(other, Int8):
            return self.value >= other.value
        return self.value >= other

    def __eq__(self, other: Union['Int8', int]) -> bool:
        if isinstance(other, Int8):
            return self.value == other.value
        return self.value == other

    def __ne__(self, other: Union['Int8', int]) -> bool:
        if isinstance(other, Int8):
            return self.value != other.value
        return self.value != other

    def __repr__(self) -> str:
        return f"Int8({self.value})"

    def __int__(self) -> int:
        return self.value

    def __neg__(self) -> 'Int8':
        return Int8(self._to_int8(-self.value))

    def __and__(self, other: Union['Int8', int]) -> 'Int8':
        if isinstance(other, Int8):
            other = other.value
        return Int8(self._to_int8(self.value & other))

    def __or__(self, other: Union['Int8', int]) -> 'Int8':
        if isinstance(other, Int8):
            other = other.value
        return Int8(self._to_int8(self.value | other))

    def __xor__(self, other: Union['Int8', int]) -> 'Int8':
        if isinstance(other, Int8):
            other = other.value
        return Int8(self._to_int8(self.value ^ other))

    def __lshift__(self, other: Union['Int8', int]) -> 'Int8':
        if isinstance(other, Int8):
            other = other.value
        return Int8(self._to_int8(self.value << other))

    def __rshift__(self, other: Union['Int8', int]) -> 'Int8':
        if isinstance(other, Int8):
            other = other.value
        return Int8(self._to_int8(self.value >> other))


class Int16():
    """Class to represent a 16-bit signed integer.
    
    Class Attributes:
        MIN: minimum value -32768
        MAX: maximum value  32767
        MASK: 16-bit mask   0xFFFF

    Supports the following operations:
        (+) addition
        (-) subtraction
        (*) multiplication
        (//) floor division
        (%) modulus
        (-) negation
        bit-wise: & | ^ << >>
        comparison: <, >, <=, >=, !=, ==
    """
    MIN  = -32768 # -2^15
    MAX  =  32767 # 2^15 - 1
    MASK = 0xFFFF # 16 bits

    def __init__(self, value: int):
        self.value = self._to_int16(value)

    def _to_int16(self, value: int) -> int:
        """Ensure the value is within the 64-bit integer range."""
        if value < self.MIN or value > self.MAX:
            value = (value + (2<<14)) % (2<<15) - (2<<14)
        return value

    def __add__(self, other: Union['Int16', int]) -> 'Int16':
        if isinstance(other, Int16):
            other = other.value
        return Int16(self._to_int16(self.value + other))

    def __sub__(self, other: Union['Int16', int]) -> 'Int16':
        if isinstance(other, Int16):
            other = other.value
        return Int16(self._to_int16(self.value - other))

    def __mul__(self, other: Union['Int16', int]) -> 'Int16':
        if isinstance(other, Int16):
            other = other.value
        return Int16(self._to_int16(self.value * other))

    def __floordiv__(self, other: Union['Int16', int]) -> 'Int16':
        if isinstance(other, Int16):
            other = other.value
        return Int16(self._to_int16(self.value // other))

    def __mod__(self, other: Union['Int16', int]) -> 'Int16':
        if isinstance(other, Int16):
            other = other.value
        return Int16(self._to_int16(self.value % other))

    def __lt__(self, other: Union['Int16', int]) -> bool:
        if isinstance(other, Int16):
            return self.value < other.value
        return self.value < other

    def __gt__(self, other: Union['Int16', int]) -> bool:
        if isinstance(other, Int16):
            return self.value > other.value
        return self.value > other

    def __le__(self, other: Union['Int16', int]) -> bool:
        if isinstance(other, Int16):
            return self.value <= other.value
        return self.value <= other

    def __ge__(self, other: Union['Int16', int]) -> bool:
        if isinstance(other, Int16):
            return self.value >= other.value
        return self.value >= other

    def __eq__(self, other: Union['Int16', int]) -> bool:
        if isinstance(other, Int16):
            return self.value == other.value
        return self.value == other

    def __ne__(self, other: Union['Int16', int]) -> bool:
        if isinstance(other, Int16):
            return self.value != other.value
        return self.value != other

    def __repr__(self) -> str:
        return f"Int16({self.value})"

    def __int__(self) -> int:
        return self.value

    def __neg__(self) -> 'Int16':
        return Int16(self._to_int16(-self.value))

    def __and__(self, other: Union['Int16', int]) -> 'Int16':
        if isinstance(other, Int16):
            other = other.value
        return Int16(self._to_int16(self.value & other))

    def __or__(self, other: Union['Int16', int]) -> 'Int16':
        if isinstance(other, Int16):
            other = other.value
        return Int16(self._to_int16(self.value | other))

    def __xor__(self, other: Union['Int16', int]) -> 'Int16':
        if isinstance(other, Int16):
            other = other.value
        return Int16(self._to_int16(self.value ^ other))

    def __lshift__(self, other: Union['Int16', int]) -> 'Int16':
        if isinstance(other, Int16):
            other = other.value
        return Int16(self._to_int16(self.value << other))

    def __rshift__(self, other: Union['Int16', int]) -> 'Int16':
        if isinstance(other, Int16):
            other = other.value
        return Int16(self._to_int16(self.value >> other))


class Int32():
    """Class to represent a 32-bit signed integer.
    
    Class Attributes:
        MIN: minimum value -2147483648
        MAX: maximum value  2147483647
        MASK: 32-bit mask   0xFFFFFFFF

    Supports the following operations:
        (+) addition
        (-) subtraction
        (*) multiplication
        (//) floor division
        (%) modulus
        (-) negation
        bit-wise: & | ^ << >>
        comparison: <, >, <=, >=, !=, ==
    """
    MIN = -2147483648 # -2^31
    MAX =  2147483647 # 2^31 - 1
    MASK = 0xFFFFFFFF # 32 bits

    def __init__(self, value: int):
        self.value = self._to_int32(value)

    def _to_int32(self, value: int) -> int:
        """Ensure the value is within the 64-bit integer range."""
        if value < self.MIN or value > self.MAX:
            value = (value + (2<<30)) % (2<<31) - (2<<30)
        return value

    def __add__(self, other: Union['Int32', int]) -> 'Int32':
        if isinstance(other, Int32):
            other = other.value
        return Int32(self._to_int32(self.value + other))

    def __sub__(self, other: Union['Int32', int]) -> 'Int32':
        if isinstance(other, Int32):
            other = other.value
        return Int32(self._to_int32(self.value - other))

    def __mul__(self, other: Union['Int32', int]) -> 'Int32':
        if isinstance(other, Int32):
            other = other.value
        return Int32(self._to_int32(self.value * other))

    def __floordiv__(self, other: Union['Int32', int]) -> 'Int32':
        if isinstance(other, Int32):
            other = other.value
        return Int32(self._to_int32(self.value // other))

    def __mod__(self, other: Union['Int32', int]) -> 'Int32':
        if isinstance(other, Int32):
            other = other.value
        return Int32(self._to_int32(self.value % other))

    def __lt__(self, other: Union['Int32', int]) -> bool:
        if isinstance(other, Int32):
            return self.value < other.value
        return self.value < other

    def __gt__(self, other: Union['Int32', int]) -> bool:
        if isinstance(other, Int32):
            return self.value > other.value
        return self.value > other

    def __le__(self, other: Union['Int32', int]) -> bool:
        if isinstance(other, Int32):
            return self.value <= other.value
        return self.value <= other

    def __ge__(self, other: Union['Int32', int]) -> bool:
        if isinstance(other, Int32):
            return self.value >= other.value
        return self.value >= other

    def __eq__(self, other: Union['Int32', int]) -> bool:
        if isinstance(other, Int32):
            return self.value == other.value
        return self.value == other

    def __ne__(self, other: Union['Int32', int]) -> bool:
        if isinstance(other, Int32):
            return self.value != other.value
        return self.value != other

    def __repr__(self) -> str:
        return f"Int32({self.value})"

    def __int__(self) -> int:
        return self.value

    def __neg__(self) -> 'Int32':
        return Int32(self._to_int32(-self.value))

    def __and__(self, other: Union['Int32', int]) -> 'Int32':
        if isinstance(other, Int32):
            other = other.value
        return Int32(self._to_int32(self.value & other))

    def __or__(self, other: Union['Int32', int]) -> 'Int32':
        if isinstance(other, Int32):
            other = other.value
        return Int32(self._to_int32(self.value | other))

    def __xor__(self, other: Union['Int32', int]) -> 'Int32':
        if isinstance(other, Int32):
            other = other.value
        return Int32(self._to_int32(self.value ^ other))

    def __lshift__(self, other: Union['Int32', int]) -> 'Int32':
        if isinstance(other, Int32):
            other = other.value
        return Int32(self._to_int32(self.value << other))

    def __rshift__(self, other: Union['Int32', int]) -> 'Int32':
        if isinstance(other, Int32):
            other = other.value
        return Int32(self._to_int32(self.value >> other))


class Int64():
    """Class to represent a 64-bit signed integer.
    
    Class Attributes:
        MIN: minimum value -9223372036854775808
        MAX: maximum value  9223372036854775807
        MASK: 64-bit mask   0xFFFFFFFFFFFFFFFF

    Supports the following operations:
        (+) addition
        (-) subtraction
        (*) multiplication
        (//) floor division
        (%) modulus
        (-) negation
        bit-wise: & | ^ << >>
        comparison: <, >, <=, >=, !=, ==
    """
    MIN = -9223372036854775808 # -2^63
    MAX =  9223372036854775807 # 2^63 - 1
    MASK = 0xFFFFFFFFFFFFFFFF  # 64 bits

    def __init__(self, value: int):
        self.value = self._to_int64(value)

    def _to_int64(self, value: int) -> int:
        """Ensure the value is within the 64-bit integer range."""
        if value < self.MIN or value > self.MAX:
            value = (value + (2<<62)) % (2<<63) - (2<<62)
        return value

    def __add__(self, other: Union['Int64', int]) -> 'Int64':
        if isinstance(other, Int64):
            other = other.value
        return Int64(self._to_int64(self.value + other))

    def __sub__(self, other: Union['Int64', int]) -> 'Int64':
        if isinstance(other, Int64):
            other = other.value
        return Int64(self._to_int64(self.value - other))

    def __mul__(self, other: Union['Int64', int]) -> 'Int64':
        if isinstance(other, Int64):
            other = other.value
        return Int64(self._to_int64(self.value * other))

    def __floordiv__(self, other: Union['Int64', int]) -> 'Int64':
        if isinstance(other, Int64):
            other = other.value
        return Int64(self._to_int64(self.value // other))

    def __mod__(self, other: Union['Int64', int]) -> 'Int64':
        if isinstance(other, Int64):
            other = other.value
        return Int64(self._to_int64(self.value % other))

    def __lt__(self, other: Union['Int64', int]) -> bool:
        if isinstance(other, Int64):
            return self.value < other.value
        return self.value < other

    def __gt__(self, other: Union['Int64', int]) -> bool:
        if isinstance(other, Int64):
            return self.value > other.value
        return self.value > other

    def __le__(self, other: Union['Int64', int]) -> bool:
        if isinstance(other, Int64):
            return self.value <= other.value
        return self.value <= other

    def __ge__(self, other: Union['Int64', int]) -> bool:
        if isinstance(other, Int64):
            return self.value >= other.value
        return self.value >= other

    def __eq__(self, other: Union['Int64', int]) -> bool:
        if isinstance(other, Int64):
            return self.value == other.value
        return self.value == other

    def __ne__(self, other: Union['Int64', int]) -> bool:
        if isinstance(other, Int64):
            return self.value != other.value
        return self.value != other

    def __repr__(self) -> str:
        return f"Int64({self.value})"

    def __int__(self) -> int:
        return self.value

    def __neg__(self) -> 'Int64':
        return Int64(self._to_int64(-self.value))

    def __and__(self, other: Union['Int64', int]) -> 'Int64':
        if isinstance(other, Int64):
            other = other.value
        return Int64(self._to_int64(self.value & other))

    def __or__(self, other: Union['Int64', int]) -> 'Int64':
        if isinstance(other, Int64):
            other = other.value
        return Int64(self._to_int64(self.value | other))

    def __xor__(self, other: Union['Int64', int]) -> 'Int64':
        if isinstance(other, Int64):
            other = other.value
        return Int64(self._to_int64(self.value ^ other))

    def __lshift__(self, other: Union['Int64', int]) -> 'Int64':
        if isinstance(other, Int64):
            other = other.value
        return Int64(self._to_int64(self.value << other))

    def __rshift__(self, other: Union['Int64', int]) -> 'Int64':
        if isinstance(other, Int64):
            other = other.value
        return Int64(self._to_int64(self.value >> other))


class UInt8():
    """Class to represent a 8-bit unsigned integer.
    
    Class Attributes:
        MIN: minimum value 0
        MAX: maximum value 255
        MASK: 8-bit mask   0xFF

    Supports the following operations:
        (+) addition
        (-) subtraction
        (*) multiplication
        (//) floor division
        (%) modulus
        (-) negation
        bit-wise: & | ^ << >>
        comparison: <, >, <=, >=, !=, ==
    """
    MIN  = 0
    MAX  = 255 # 2^8 - 1
    MASK = 0xFF # 8 bits

    def __init__(self, value: int):
        self.value = self._to_uint8(value)

    def _to_uint8(self, value: int) -> int:
        """Ensure the value is within the 64-bit integer range."""
        if value < self.MIN or value > self.MAX:
            value = value & self.MASK
        return value

    def __add__(self, other: Union['UInt8', int]) -> 'UInt8':
        if isinstance(other, UInt8):
            other = other.value
        return UInt8(self._to_uint8(self.value + other))

    def __sub__(self, other: Union['UInt8', int]) -> 'UInt8':
        if isinstance(other, UInt8):
            other = other.value
        return UInt8(self._to_uint8(self.value - other))

    def __mul__(self, other: Union['UInt8', int]) -> 'UInt8':
        if isinstance(other, UInt8):
            other = other.value
        return UInt8(self._to_uint8(self.value * other))

    def __floordiv__(self, other: Union['UInt8', int]) -> 'UInt8':
        if isinstance(other, UInt8):
            other = other.value
        return UInt8(self._to_uint8(self.value // other))

    def __mod__(self, other: Union['UInt8', int]) -> 'UInt8':
        if isinstance(other, UInt8):
            other = other.value
        return UInt8(self._to_uint8(self.value % other))

    def __lt__(self, other: Union['UInt8', int]) -> bool:
        if isinstance(other, UInt8):
            return self.value < other.value
        return self.value < other

    def __gt__(self, other: Union['UInt8', int]) -> bool:
        if isinstance(other, UInt8):
            return self.value > other.value
        return self.value > other

    def __le__(self, other: Union['UInt8', int]) -> bool:
        if isinstance(other, UInt8):
            return self.value <= other.value
        return self.value <= other

    def __ge__(self, other: Union['UInt8', int]) -> bool:
        if isinstance(other, UInt8):
            return self.value >= other.value
        return self.value >= other

    def __eq__(self, other: Union['UInt8', int]) -> bool:
        if isinstance(other, UInt8):
            return self.value == other.value
        return self.value == other

    def __ne__(self, other: Union['UInt8', int]) -> bool:
        if isinstance(other, UInt8):
            return self.value != other.value
        return self.value != other

    def __repr__(self) -> str:
        return f"UInt8({self.value})"

    def __int__(self) -> int:
        return self.value

    def __neg__(self) -> 'UInt8':
        return UInt8(self._to_uint8(-self.value))

    def __and__(self, other: Union['UInt8', int]) -> 'UInt8':
        if isinstance(other, UInt8):
            other = other.value
        return UInt8(self._to_uint8(self.value & other))

    def __or__(self, other: Union['UInt8', int]) -> 'UInt8':
        if isinstance(other, UInt8):
            other = other.value
        return UInt8(self._to_uint8(self.value | other))

    def __xor__(self, other: Union['UInt8', int]) -> 'UInt8':
        if isinstance(other, UInt8):
            other = other.value
        return UInt8(self._to_uint8(self.value ^ other))

    def __lshift__(self, other: Union['UInt8', int]) -> 'UInt8':
        if isinstance(other, UInt8):
            other = other.value
        return UInt8(self._to_uint8(self.value << other))

    def __rshift__(self, other: Union['UInt8', int]) -> 'UInt8':
        if isinstance(other, UInt8):
            other = other.value
        return UInt8(self._to_uint8(self.value >> other))


class UInt16():
    """Class to represent a 16-bit unsigned integer.
    
    Class Attributes:
        MIN: minimum value 0
        MAX: maximum value 65535
        MASK: 16-bit mask  0xFFFF

    Supports the following operations:
        (+) addition
        (-) subtraction
        (*) multiplication
        (//) floor division
        (%) modulus
        (-) negation
        bit-wise: & | ^ << >>
        comparison: <, >, <=, >=, !=, ==
    """
    MIN  = 0
    MAX  = 65535 # 2^16 - 1
    MASK = 0xFFFF # 16 bits

    def __init__(self, value: int):
        self.value = self._to_uint16(value)

    def _to_uint16(self, value: int) -> int:
        """Ensure the value is within the 64-bit integer range."""
        if value < self.MIN or value > self.MAX:
            value = value & self.MASK
        return value

    def __add__(self, other: Union['UInt16', int]) -> 'UInt16':
        if isinstance(other, UInt16):
            other = other.value
        return UInt16(self._to_uint16(self.value + other))

    def __sub__(self, other: Union['UInt16', int]) -> 'UInt16':
        if isinstance(other, UInt16):
            other = other.value
        return UInt16(self._to_uint16(self.value - other))

    def __mul__(self, other: Union['UInt16', int]) -> 'UInt16':
        if isinstance(other, UInt16):
            other = other.value
        return UInt16(self._to_uint16(self.value * other))

    def __floordiv__(self, other: Union['UInt16', int]) -> 'UInt16':
        if isinstance(other, UInt16):
            other = other.value
        return UInt16(self._to_uint16(self.value // other))

    def __mod__(self, other: Union['UInt16', int]) -> 'UInt16':
        if isinstance(other, UInt16):
            other = other.value
        return UInt16(self._to_uint16(self.value % other))

    def __lt__(self, other: Union['UInt16', int]) -> bool:
        if isinstance(other, UInt16):
            return self.value < other.value
        return self.value < other

    def __gt__(self, other: Union['UInt16', int]) -> bool:
        if isinstance(other, UInt16):
            return self.value > other.value
        return self.value > other

    def __le__(self, other: Union['UInt16', int]) -> bool:
        if isinstance(other, UInt16):
            return self.value <= other.value
        return self.value <= other

    def __ge__(self, other: Union['UInt16', int]) -> bool:
        if isinstance(other, UInt16):
            return self.value >= other.value
        return self.value >= other

    def __eq__(self, other: Union['UInt16', int]) -> bool:
        if isinstance(other, UInt16):
            return self.value == other.value
        return self.value == other

    def __ne__(self, other: Union['UInt16', int]) -> bool:
        if isinstance(other, UInt16):
            return self.value != other.value
        return self.value != other

    def __repr__(self) -> str:
        return f"UInt16({self.value})"

    def __int__(self) -> int:
        return self.value

    def __neg__(self) -> 'UInt16':
        return UInt16(self._to_uint16(-self.value))

    def __and__(self, other: Union['UInt16', int]) -> 'UInt16':
        if isinstance(other, UInt16):
            other = other.value
        return UInt16(self._to_uint16(self.value & other))

    def __or__(self, other: Union['UInt16', int]) -> 'UInt16':
        if isinstance(other, UInt16):
            other = other.value
        return UInt16(self._to_uint16(self.value | other))

    def __xor__(self, other: Union['UInt16', int]) -> 'UInt16':
        if isinstance(other, UInt16):
            other = other.value
        return UInt16(self._to_uint16(self.value ^ other))

    def __lshift__(self, other: Union['UInt16', int]) -> 'UInt16':
        if isinstance(other, UInt16):
            other = other.value
        return UInt16(self._to_uint16(self.value << other))

    def __rshift__(self, other: Union['UInt16', int]) -> 'UInt16':
        if isinstance(other, UInt16):
            other = other.value
        return UInt16(self._to_uint16(self.value >> other))


class UInt32():
    """Class to represent a 32-bit unsigned integer.
    
    Class Attributes:
        MIN: minimum value 0
        MAX: maximum value 4294967295
        MASK: 32-bit mask  0xFFFFFFFF

    Supports the following operations:
        (+) addition
        (-) subtraction
        (*) multiplication
        (//) floor division
        (%) modulus
        (-) negation
        bit-wise: & | ^ << >>
        comparison: <, >, <=, >=, !=, ==
    """
    MIN  = 0
    MAX  = 4294967295 # 2^32 - 1
    MASK = 0xFFFFFFFF # 32 bits

    def __init__(self, value: int):
        self.value = self._to_uint32(value)

    def _to_uint32(self, value: int) -> int:
        """Ensure the value is within the 64-bit integer range."""
        if value < self.MIN or value > self.MAX:
            value = value & self.MASK
        return value

    def __add__(self, other: Union['UInt32', int]) -> 'UInt32':
        if isinstance(other, UInt32):
            other = other.value
        return UInt32(self._to_uint32(self.value + other))

    def __sub__(self, other: Union['UInt32', int]) -> 'UInt32':
        if isinstance(other, UInt32):
            other = other.value
        return UInt32(self._to_uint32(self.value - other))

    def __mul__(self, other: Union['UInt32', int]) -> 'UInt32':
        if isinstance(other, UInt32):
            other = other.value
        return UInt32(self._to_uint32(self.value * other))

    def __floordiv__(self, other: Union['UInt32', int]) -> 'UInt32':
        if isinstance(other, UInt32):
            other = other.value
        return UInt32(self._to_uint32(self.value // other))

    def __mod__(self, other: Union['UInt32', int]) -> 'UInt32':
        if isinstance(other, UInt32):
            other = other.value
        return UInt32(self._to_uint32(self.value % other))

    def __lt__(self, other: Union['UInt32', int]) -> bool:
        if isinstance(other, UInt32):
            return self.value < other.value
        return self.value < other

    def __gt__(self, other: Union['UInt32', int]) -> bool:
        if isinstance(other, UInt32):
            return self.value > other.value
        return self.value > other

    def __le__(self, other: Union['UInt32', int]) -> bool:
        if isinstance(other, UInt32):
            return self.value <= other.value
        return self.value <= other

    def __ge__(self, other: Union['UInt32', int]) -> bool:
        if isinstance(other, UInt32):
            return self.value >= other.value
        return self.value >= other

    def __eq__(self, other: Union['UInt32', int]) -> bool:
        if isinstance(other, UInt32):
            return self.value == other.value
        return self.value == other

    def __ne__(self, other: Union['UInt32', int]) -> bool:
        if isinstance(other, UInt32):
            return self.value != other.value
        return self.value != other

    def __repr__(self) -> str:
        return f"UInt32({self.value})"

    def __int__(self) -> int:
        return self.value

    def __neg__(self) -> 'UInt32':
        return UInt32(self._to_uint32(-self.value))

    def __and__(self, other: Union['UInt32', int]) -> 'UInt32':
        if isinstance(other, UInt32):
            other = other.value
        return UInt32(self._to_uint32(self.value & other))

    def __or__(self, other: Union['UInt32', int]) -> 'UInt32':
        if isinstance(other, UInt32):
            other = other.value
        return UInt32(self._to_uint32(self.value | other))

    def __xor__(self, other: Union['UInt32', int]) -> 'UInt32':
        if isinstance(other, UInt32):
            other = other.value
        return UInt32(self._to_uint32(self.value ^ other))

    def __lshift__(self, other: Union['UInt32', int]) -> 'UInt32':
        if isinstance(other, UInt32):
            other = other.value
        return UInt32(self._to_uint32(self.value << other))

    def __rshift__(self, other: Union['UInt32', int]) -> 'UInt32':
        if isinstance(other, UInt32):
            other = other.value
        return UInt32(self._to_uint32(self.value >> other))


class UInt64():
    """Class to represent a 64-bit unsigned integer.
    
    Class Attributes:
        MIN: minimum value 0
        MAX: maximum value 18446744073709551615
        MASK: 64-bit mask  0xFFFFFFFFFFFFFFFF

    Supports the following operations:
        (+) addition
        (-) subtraction
        (*) multiplication
        (//) floor division
        (%) modulus
        (-) negation
        bit-wise: & | ^ << >>
        comparison: <, >, <=, >=, !=, ==
    """
    MIN  = 0
    MAX  = 18446744073709551615 # 2^64 - 1
    MASK = 0xFFFFFFFFFFFFFFFF  # 64 bits

    def __init__(self, value: int):
        self.value = self._to_uint64(value)

    def _to_uint64(self, value: int) -> int:
        """Ensure the value is within the 64-bit integer range."""
        if value < self.MIN or value > self.MAX:
            value = value & self.MASK
        return value

    def __add__(self, other: Union['UInt64', int]) -> 'UInt64':
        if isinstance(other, UInt64):
            other = other.value
        return UInt64(self._to_uint64(self.value + other))

    def __sub__(self, other: Union['UInt64', int]) -> 'UInt64':
        if isinstance(other, UInt64):
            other = other.value
        return UInt64(self._to_uint64(self.value - other))

    def __mul__(self, other: Union['UInt64', int]) -> 'UInt64':
        if isinstance(other, UInt64):
            other = other.value
        return UInt64(self._to_uint64(self.value * other))

    def __floordiv__(self, other: Union['UInt64', int]) -> 'UInt64':
        if isinstance(other, UInt64):
            other = other.value
        return UInt64(self._to_uint64(self.value // other))

    def __mod__(self, other: Union['UInt64', int]) -> 'UInt64':
        if isinstance(other, UInt64):
            other = other.value
        return UInt64(self._to_uint64(self.value % other))

    def __lt__(self, other: Union['UInt64', int]) -> bool:
        if isinstance(other, UInt64):
            return self.value < other.value
        return self.value < other

    def __gt__(self, other: Union['UInt64', int]) -> bool:
        if isinstance(other, UInt64):
            return self.value > other.value
        return self.value > other

    def __le__(self, other: Union['UInt64', int]) -> bool:
        if isinstance(other, UInt64):
            return self.value <= other.value
        return self.value <= other

    def __ge__(self, other: Union['UInt64', int]) -> bool:
        if isinstance(other, UInt64):
            return self.value >= other.value
        return self.value >= other

    def __eq__(self, other: Union['UInt64', int]) -> bool:
        if isinstance(other, UInt64):
            return self.value == other.value
        return self.value == other

    def __ne__(self, other: Union['UInt64', int]) -> bool:
        if isinstance(other, UInt64):
            return self.value != other.value
        return self.value != other

    def __repr__(self) -> str:
        return f"UInt64({self.value})"

    def __int__(self) -> int:
        return self.value

    def __neg__(self) -> 'UInt64':
        return UInt64(self._to_uint64(-self.value))

    def __and__(self, other: Union['UInt64', int]) -> 'UInt64':
        if isinstance(other, UInt64):
            other = other.value
        return UInt64(self._to_uint64(self.value & other))

    def __or__(self, other: Union['UInt64', int]) -> 'UInt64':
        if isinstance(other, UInt64):
            other = other.value
        return UInt64(self._to_uint64(self.value | other))

    def __xor__(self, other: Union['UInt64', int]) -> 'UInt64':
        if isinstance(other, UInt64):
            other = other.value
        return UInt64(self._to_uint64(self.value ^ other))

    def __lshift__(self, other: Union['UInt64', int]) -> 'UInt64':
        if isinstance(other, UInt64):
            other = other.value
        return UInt64(self._to_uint64(self.value << other))

    def __rshift__(self, other: Union['UInt64', int]) -> 'UInt64':
        if isinstance(other, UInt64):
            other = other.value
        return UInt64(self._to_uint64(self.value >> other))
