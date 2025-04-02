"""
"""
import socket

from ipaddress import IPv4Address, ip_address
# pylint: disable=no-name-in-module
from socket import AddressFamily
# pylint: enable=no-name-in-module
from typing import Any, Union

# typedef
_DictKey = Union[str, int, float, bool, bytes, tuple, frozenset]
_ValidDict = dict[_DictKey, Any]

def get_family_from_address(address: str) -> AddressFamily | None:
    """Returns the address family IPv4 or IPv6"""
    try:
        if isinstance(ip_address(address), IPv4Address):
            return socket.AF_INET

        return socket.AF_INET6

    except ValueError:
        return None

def change_dict_key(old_key: _DictKey,
                    new_key: _DictKey,
                    target_dict: _ValidDict) -> bool:
    """Changes a dictionary key to a newly specified one.
    
    Args:
        old_key: The key to be changed.
        new_key: The new value of the key.
        target_dict: The dictionary to be changed.
    
    Returns:
        True if the key was changed.

    """
    if new_key in target_dict.keys():
        return False

    item = target_dict[old_key]
    del target_dict[old_key]
    target_dict[new_key] = item

    return True
