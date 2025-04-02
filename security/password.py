"""
"""
import hashlib
from typing import Callable, Final, Literal, Tuple

# constants
MIN_USERNAME_LEN: Final[int] = 4
MIN_PASSWORD_LEN: Final[int] = 6

# typedef
_UserNamePassword = Tuple[str, str]

def create_username_and_password(
    user_name: str,
    password: str,
    min_name_length: int                          = MIN_USERNAME_LEN,
    name_format: Literal['isalpha', 'isalnum']    = 'isalnum',
    hash_func: Callable[[str, bool],
                        'hashlib._hashlib._Hash'] = hashlib.sha256) -> _UserNamePassword | None:
    """Validate a user name and password.
    
    Use Validation.validate_password_complexity() to validate a password
    before calling this function.

    Args:
        user_name: The user name.
        password: The plain text password.
        min_name_length: The minimum length the of the user name.
        name_format: Whether the user name should be alphabetic or alphanumeric
        hash_func: Which hash function from hashlib to use.
    
    Returns
        A _UserNamePassword or None if supplied user name is invalid.
    """
    func: Callable[[str], bool] = str.isalpha
    if name_format == 'isalnum':
        func = str.isalnum

    if len(user_name) <= min_name_length:
        return None

    if not func(user_name):
        return None

    hash_pass = hash_func(password.encode('utf-8')).hexdigest()

    return (user_name, hash_pass)