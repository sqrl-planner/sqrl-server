"""Helper functions."""
from typing import Optional


def to_int(x: str) -> Optional[int]:
    """
    Converts a value to an integer, while silently handling a None value.

    >>> to_int('7')
    7
    >>> to_int(None)
    None
    """
    if x is None:
        return x
    else:
        return int(x)
