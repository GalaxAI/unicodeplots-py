from dataclasses import dataclass
from typing import Callable


@dataclass
class CanvasParams:
    """Parameters for the plotting canvas."""
    width: int = 128
    height: int = 64
    resolution: float = 1.0
    origin_x: float = 0.0
    origin_y: float = 0.0
    xflip: bool = False
    yflip: bool = False
    blend: bool = True
    xscale: Callable[[float], float] = lambda x: x
    yscale: Callable[[float], float] = lambda y: y