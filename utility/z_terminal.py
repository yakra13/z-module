"""
"""
import getpass
import hashlib
import signal
from typing import Callable, Literal
from z_types import _UserNamePassword

def get_username_and_password(
    min_name_length: int                       = 4,
    min_password_length: int                   = 4,
    reenter_password: bool                     = True,
    name_format: Literal['isalpha', 'isalnum'] = 'isalpha',
    hash_func: Callable[[str, bool], 'hashlib._hashlib._Hash']
                                               = hashlib.sha256) -> _UserNamePassword | None:
    """ Prompt a user to input user name and password.

        Additionally hashes the password with the provided hash function.

    Args:
        min_name_length: minimum required name length
        min_password_length: minimum required password length
        name_format: name check alpha or alpha-numeric
        hash_func: function to use for password hashing

    Raises:
        KeyboardInterrupt: Raised when pressing ctrl+c to cancel

    Returns:
        _UserNamePassword: tuple containing the (name, hashed password)
        None: returned when exiting early with ctrl+c
    """
    def signal_handler(signum, frame):
        """Handles early exit of this function."""
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, signal_handler)

    user_name: str = ''
    user_pass: str = ''
    func: Callable[[str], bool] = str.isalpha

    if name_format == 'isalnum':
        func = str.isalnum

    try:
        while user_name := input('Enter a user name: '):
            if len(user_name) <= min_name_length:
                print(f'Name must be at least {min_name_length} characters.')
                continue
            if not func(user_name):
                if name_format == 'isalnum':
                    print('User name may contain only: [a-z] [A-Z] [0-9].')
                else:
                    print('User name may contain only: [a-z] [A-Z].')
                continue
            break
    except KeyboardInterrupt:
        return None

    try:
        while user_pass := getpass.getpass('Enter a password: '):
            if len(user_pass) < min_password_length:
                print(f'Password must be at least {min_password_length} characters.')
            else:
                if reenter_password:
                    if user_pass == getpass.getpass('Reenter password: '):
                        break
                    else:
                        print('Passwords did not match.')
                break
        hash_pass = hash_func(user_pass.encode('utf-8')).hexdigest()
        # delete the clear text password (probably not necessary)
        del user_pass
    except KeyboardInterrupt:
        return None

    return (user_name, hash_pass)
