"""Helper functions."""
from typing import Any, Callable, Optional


def nullable_convert(value: Any, func: Callable[[Any], Any]) -> Any:
    """Convert a value given a conversion function, while silently handling an input of None."""
    if value is None:
        return value
    else:
        return func(value)

    
def int_or_none(value: Any) -> Optional[int]:
    """Converts a value to an integer, while silently handling a None value.

    >>> to_int('7')
    7
    >>> to_int(None)
    None
    """
    return nullable_convert(value, int)
