"""
Custom validation.
"""
import functools
import inspect
import re
from ipaddress import ip_address
import types
from typing import Any, Callable, Final, Iterable, Tuple, Type, TypeVar, Union
from typing import get_type_hints
from typing import _GenericAlias

from z_module.utility.z_base import Singleton

# _AddressPort = Tuple[str, int]
F = TypeVar('F', bound=Callable[..., Any])

PORTS_RANGE: Final[Tuple[int, int]] = (1024, 65535)
REGEX_PASSWORD: Final[str] = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$"

def enforce_parameter_types(ignore_args_kwargs: Union[F, bool] = True) -> Callable[[F], F]:
    """Decorator to enforce typing on functions and methods.

    @classmethod must come before this decorator to work properly.

    Args:
        ignore_args_kwargs: If true type hints are not required on args/kwargs parameters

    Raises:
        TypeError: An argument passed to this function does not match the parameter type hint
    """
    # Check if decorator was called without arguments
    if callable(ignore_args_kwargs):
        func = ignore_args_kwargs
        return _enforce_parameter_types(func, True)
    else:
        # If called with arguments set wrap it in decorator function
        def decorator(func: F) -> F:
            return _enforce_parameter_types(func, ignore_args_kwargs)
        return decorator

def _enforce_parameter_types(func: F, ignore_args_kwargs: bool) -> F:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        f_name = func.__qualname__
        signature = inspect.signature(func)
        type_hints: dict[str, Any] = get_type_hints(func)
        args_copy = args
        #TODO: does not handle kwargs
        # kwargs_copy = kwargs
        # Check if it is a method vs a function and strip cls/self variable
        if '.' in f_name:
            args_copy = args_copy[1:]

        # Check if there are parameters
        if len(args_copy) == 0 and len(kwargs) == 0:
            return func(*args, **kwargs)

        # Validate that all parameters are type hinted (ignore *args, and **kwargs)
        for p in signature.parameters.values():
            if p.name in ('self', 'cls'):
                continue
            if ignore_args_kwargs and p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD):
                continue
            if p.name not in type_hints:
                raise TypeError(f'{f_name}() parameter \'{p.name}\' is not type hinted.')

        arg_index: int = 0
        # Iterate over the type hints and check that the args are matching
        for p_name, p_hint in type_hints.items():
            # Ignore the return type in the type hints
            if arg_index >= len(args_copy) or p_name == 'return':
                break

            arg = args_copy[arg_index]

            a_type = type(arg)
            a_name, a_hint = _get_variable_name_and_type_hint(arg)

            # Determine if arg is a literal value or a variable
            if a_name is None:
                a_name = 'Literal value'

            if not validate_type_hints_recursive(arg, p_hint):
                err = f'{a_name} passed to {f_name}({p_name}: {p_hint}) was not correctly typed.\n'
                err += f'\tVariable => {a_name}\n'
                err += f'\tType Hint => {a_hint}\n'
                err += f'\tActual Type => {a_type}'
                print(f'FAIL\t{f_name} TypeError')
                raise TypeError(err)

            arg_index += 1
        return func(*args, **kwargs)
    return wrapper

def _get_variable_name_and_type_hint(var: Any) -> Tuple[str, type]:
    frame = inspect.currentframe().f_back
    frame = frame.f_back
    annotations = frame.f_globals.get('__annotations__', {})
    var_name: str = ''
    var_type: type = None
    try:
        # while frame:
        variables = frame.f_locals
        for name, value in variables.items():
            if value is var:
                var_name = name
                var_type = annotations.get(var_name, None)
                return (var_name, var_type)
            # frame = frame.f_back
        return None, None
    finally:
        del frame

def validate_type_hints_recursive(obj: Any, expected_type: _GenericAlias) -> bool:
    """Recursive validation of type hinted parameters against some argument.

    Will recurse thru iterable type hints ensuring all values match the specified
    type hinted parameter.

    Args:
        obj: object to check against expected type hint
        expected_type: expects _GenericAlias from get_type_hints()
    
    Returns:
        True if the object fully matches the type hint.
    """
    if isinstance(expected_type, _GenericAlias) or \
       isinstance(expected_type, types.GenericAlias):
        if expected_type.__origin__ == dict:
            if not isinstance(obj, dict):
                return False

            k_type, v_type = expected_type.__args__
            # Check the values
            for value in obj.values():
                if not validate_type_hints_recursive(value, v_type):
                    return False
            # Check the keys
            for key in obj.keys():
                if not validate_type_hints_recursive(key, k_type):
                    return False
            return True

        elif isinstance(expected_type, Iterable):
            if not isinstance(obj, Iterable):
                return False

            for item in obj:
                if not validate_type_hints_recursive(item, expected_type.__args__[0]):
                    return False
            return True

    elif isinstance(expected_type, types.UnionType):
        #TODO: i believe in a list[str | int] it checks that they are all str or all int
        # not a combination of the two
        for et in expected_type.__args__:
            if validate_type_hints_recursive(obj, et):
                return True
        return False

    return isinstance(obj, expected_type)


class Validate(Singleton):
    """Validation class.
    
    Supports method chaining.

    Usage:
        Is my_int an int type with a value from 0 to 100
        Val.start(my_int).is_type(int).in_range(0, 100)

        Is my_str a str type from 'a' to 'z' and cannot be an empty string
        Val.start(my_str).is_type(str).in_range('a', 'z').not_empty()
    
    """
    _var_name: str = None
    _variable: Any = None

    @classmethod
    def start(cls, var: Any, param_name: str = None):
        """Must be called first in the method chain.

        Args:
            var: The variable to validate.
            param_name: If supplied this name will be used instead of the parameter's actual name.
        
        Raises:
            ValueError: The variable is None
        """
        cls._variable = var
        if param_name is None:
            cls._var_name = cls._get_variable_name(cls._variable)
        else:
            cls._var_name = param_name
        if var is None:
            err = 'start() parameter \'var\' can not be None.'
            cls._reset()
            raise ValueError(err)
        return cls

    @classmethod
    def regex_str(cls, pattern: str = REGEX_PASSWORD):
        """Validates that a string conforms to a regex pattern.
        
        Args:
            pattern: A regex pattern to match
        
        Raises:
            RuntimeError: start() was not called first
            TypeError: The variable is not a valid type (str)
            ValueError: The variable does not match the pattern
        """
        if cls._variable is None:
            raise RuntimeError('start() method must be called first')

        pattern = re.compile(pattern)

        try:
            if not bool(pattern.match(cls._variable)):
                err = f'{cls._var_name} does not match {pattern}'
                cls._reset()
                raise ValueError(err)
        except TypeError as exc:
            raise TypeError('Only str are valid for str_contains_chars()') from exc

        return cls

    @classmethod
    def not_empty(cls):
        """Validates that the variable is not empty.
        
        Raises:
            RuntimeError: start() was not called first
            ValueError: The variable is empty.
        """
        if cls._variable is None:
            raise RuntimeError('start() method must be called first')

        if not cls._variable:
            err = f'{cls._var_name} is empty.'
            cls._reset()
            raise ValueError(err)
        return cls

    @classmethod
    def in_range(cls, minimum: Any, maximum: Any):
        """Validate the variable is within a specified range.

        Args:
            minimum: Inclusive minimum value for the variable
            maximum: Inclusive maximum value for the variable

        Raises:
            RuntimeError: start() was not called first
            TypeError: Variable type is not supported
            ValueError: Variable is not within the range
        """
        if cls._variable is None:
            raise RuntimeError('start() method must be called first')

        try:
            if cls._variable < minimum or cls._variable > maximum:
                err = f'{cls._var_name}: ({cls._variable}) is not within ' \
                                 f'the range of ({minimum} - {maximum})'
                cls._reset()
                raise ValueError(err)
        except TypeError as exc:
            err = f'{cls._var_name} of {type(cls._variable)} does not ' \
                            'support the in range operation.'
            cls._reset()
            raise TypeError(err) from exc

        return cls

    @classmethod
    def length_in_range(cls, minimum: int, maximum: int):
        """Validates the length of the variable is within a specified range.

        Args:
            minimum: Inclusive minimum value for the variable length
            maximum: Inclusive maximum value for the variable length

        Raises:
            RuntimeError: start() was not called first
            TypeError: Variable type does not supported len()
            ValueError: Variable length is not within the range
        """
        if cls._variable is None:
            raise RuntimeError('start() method must be called first')

        try:
            length = len(cls._variable)
            if length < minimum or length > maximum:
                err = f'{cls._var_name} length is not within ' \
                                 f'the range of ({minimum} - {maximum})'
                cls._reset()
                raise ValueError(err)
        except TypeError as exc:
            err = f'{cls._var_name} of {type(cls._variable)} does not ' \
                            'support the len() function.'
            cls._reset()
            raise TypeError(err) from exc

        return cls

    @ classmethod
    def is_type(cls, var_type: Type):
        """Validates the type of the variable.

        Args:
            var_type: The expected type of the variable

        Raises:
            RuntimeError: start() was not called first
            TypeError: Variable is not of the specified type
        """
        if cls._variable is None:
            raise RuntimeError('start() method must be called first')

        if not isinstance(cls._variable, var_type):
            err = f'{cls._var_name} expected type {var_type},' \
                'instead received type {type(cls._variable)}'
            cls._reset()
            raise TypeError(err)
        return cls

    @classmethod
    def is_ip_address(cls):
        """Validates that the passed in string is an IPv4/IPv6 address.

        Raises:
            RuntimeError: start() was not called first
            ValueError: Variable does not conform to an IP address
        """
        if cls._variable is None:
            raise RuntimeError('start() method must be called first')

        try:
            _ = ip_address(cls._variable)
        except ValueError as exc:
            err = f'{cls._var_name} is not a valid IP address.'
            cls._reset()
            raise ValueError(err) from exc

        return cls

    @classmethod
    def _reset(cls) -> None:
        cls._variable = None
        cls._var_name = None

    @classmethod
    def _get_variable_name(cls, var: Any) -> str:
        frame = inspect.currentframe()
        frame = frame.f_back
        frame = frame.f_back
        try:
            while frame:
                variables = frame.f_locals
                for name, value in variables.items():
                    if value is var:
                        return name
                frame = frame.f_back
        finally:
            del frame
