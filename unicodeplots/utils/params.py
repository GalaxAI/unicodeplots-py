from dataclasses import dataclass, field, fields
from functools import wraps
from typing import Any, Callable, Type, TypeVar, cast

T = TypeVar("T")


def dataclass_filter_kwargs(cls: Type[T]) -> Type[T]:
    """Decorator to create a dataclass that ignores invalid kwargs"""
    cls = dataclass(cls)

    original_init = cls.__init__

    # Define our new __init__
    # TODO: Handle missing kwargs,
    @wraps(original_init)
    def __init__(self: Any, **kwargs: Any) -> None:
        valid_fields = {f.name for f in fields(cast("type[Any]", cls))}
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_fields}
        original_init(self, **filtered_kwargs)

    setattr(cls, "__init__", __init__)

    return cls


@dataclass_filter_kwargs
class CanvasParams:
    """Parameters for the plotting canvas."""

    width: int = 128
    height: int = 64
    resolution: float = 1.0
    origin_x: float = 0.0
    origin_y: float = 0.0
    xflip: bool = False
    yflip: bool = False
    xscale: Callable[[float], float] = field(default_factory=lambda: lambda x: x)
    yscale: Callable[[float], float] = field(default_factory=lambda: lambda y: y)


@dataclass_filter_kwargs
class BoxParams:
    """Params for the box."""

    border: str = "single"
    title: str = "Title"
    xlabel: str = "x"
    ylabel: str = "y"
    legend: bool = False
