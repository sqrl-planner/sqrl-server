"""Helper functions."""

def to_int(x):
    """
    Converts a value to an integer, while silently handling a None value.

    >>> to_int('7')
    7
    >>> to_int(None)
    None
    """
    if x is None: return x
    return int(x)