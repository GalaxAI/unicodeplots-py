from __future__ import annotations

from functools import wraps
from time import perf_counter
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def time_execution(func: Callable[P, R]) -> Callable[P, tuple[R, float]]:
    """
    Wrap a callable so its execution time is measured.

    The wrapped callable returns a tuple containing the original result and the elapsed
    time in seconds, enabling callers to manage timing information explicitly.
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> tuple[R, float]:
        start = perf_counter()
        result = func(*args, **kwargs)
        return result, perf_counter() - start

    return wrapper
