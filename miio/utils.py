import functools
import inspect
import warnings
from datetime import datetime, timedelta
from typing import Tuple


def deprecated(reason):
    """
    This is a decorator which can be used to mark functions and classes
    as deprecated. It will result in a warning being emitted
    when the function is used.

    From https://stackoverflow.com/a/40301488
    """

    string_types = (type(b""), type(u""))
    if isinstance(reason, string_types):

        # The @deprecated is used with a 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated("please, use another function")
        #    def old_function(x, y):
        #      pass

        def decorator(func1):

            if inspect.isclass(func1):
                fmt1 = "Call to deprecated class {name} ({reason})."
            else:
                fmt1 = "Call to deprecated function {name} ({reason})."

            @functools.wraps(func1)
            def new_func1(*args, **kwargs):
                warnings.simplefilter("always", DeprecationWarning)
                warnings.warn(
                    fmt1.format(name=func1.__name__, reason=reason),
                    category=DeprecationWarning,
                    stacklevel=2,
                )
                warnings.simplefilter("default", DeprecationWarning)
                return func1(*args, **kwargs)

            return new_func1

        return decorator

    elif inspect.isclass(reason) or inspect.isfunction(reason):

        # The @deprecated is used without any 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated
        #    def old_function(x, y):
        #      pass

        func2 = reason

        if inspect.isclass(func2):
            fmt2 = "Call to deprecated class {name}."
        else:
            fmt2 = "Call to deprecated function {name}."

        @functools.wraps(func2)
        def new_func2(*args, **kwargs):
            warnings.simplefilter("always", DeprecationWarning)
            warnings.warn(
                fmt2.format(name=func2.__name__),
                category=DeprecationWarning,
                stacklevel=2,
            )
            warnings.simplefilter("default", DeprecationWarning)
            return func2(*args, **kwargs)

        return new_func2

    else:
        raise TypeError(repr(type(reason)))


def pretty_seconds(x: float) -> timedelta:
    """Return a timedelta object from seconds."""
    return timedelta(seconds=x)


def pretty_time(x: float) -> datetime:
    """Return a datetime object from unix timestamp."""
    return datetime.fromtimestamp(x)


def int_to_rgb(x: int) -> Tuple[int, int, int]:
    """Return a RGB tuple from integer."""
    red = (x >> 16) & 0xFF
    green = (x >> 8) & 0xFF
    blue = x & 0xFF
    return red, green, blue


def rgb_to_int(x: Tuple[int, int, int]) -> int:
    """Return an integer from RGB tuple."""
    return int(x[0] << 16 | x[1] << 8 | x[2])


def int_to_brightness(x: int) -> int:
    """"Return brightness (0-100) from integer."""
    return x >> 24


def brightness_and_color_to_int(brightness: int, color: Tuple[int, int, int]) -> int:
    return int(brightness << 24 | color[0] << 16 | color[1] << 8 | color[2])
