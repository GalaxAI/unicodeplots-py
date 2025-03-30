import math
from abc import ABC, abstractmethod
from typing import Any, Callable, List

from unicodeplots.utils import CanvasParams, Color, ColorType


class Canvas(ABC):
    _x_pixels = 1
    _y_pixels = 1
    default_char = 0x2800
    default_color = Color.WHITE

    def __init__(self, **kwargs):
        self._params = CanvasParams(**kwargs)

        # Calculate pixel dimensions based on logical dimensions and resolution
        self.pixel_width = math.ceil(self.width * self.resolution)
        self.pixel_height = math.ceil(self.height * self.resolution)

        # Ensure pixel dimensions are multiples of character cell dimensions
        self.pixel_width = self._align_to_char_length(self.pixel_width)
        self.pixel_height = self._align_to_char_length(self.pixel_height)

        self.grid_rows = self.pixel_height // self.y_pixel_per_char
        self.grid_cols = self.pixel_width // self.x_pixel_per_char

        self.active_cells: List[List[Any]] = [[] for _ in range(self.grid_rows)]
        self.active_colors: List[List[ColorType]] = [[] for _ in range(self.grid_rows)]

    def _align_to_char_length(self, length: int) -> int:
        """Ensure length is aligned to character cell boundaries"""
        remainder = length % self.x_pixel_per_char
        if remainder > 0:
            return length + (self.x_pixel_per_char - remainder)
        return length

    @property
    def x_pixel_per_char(self) -> int:
        return self._x_pixels

    @property
    def y_pixel_per_char(self) -> int:
        return self._y_pixels

    # NOTE This might be deprecated.
    def _set_pixel(self, px: int, py: int, color: ColorType):
        """Set a pixel in the Braille grid representation."""

    @abstractmethod
    def line(self, x1: float, y1: float, x2: float, y2: float, color: ColorType):
        """Draw a line between logical coordinates (x1,y1) and (x2,y2)"""

    @abstractmethod
    def render(self) -> str:
        """Rendering of canvas to string"""

    def x_to_pixel(self, x: float) -> float:
        """Convert logical x coordinate to pixel space"""
        if self.xflip:
            return (1 - (x - self.origin_x) / self.width) * self.pixel_width
        return ((x - self.origin_x) / self.width) * self.pixel_width

    def y_to_pixel(self, y: float) -> float:
        """Convert logical y coordinate to pixel space"""
        if self.yflip:
            return (y - self.origin_y) / self.height * self.pixel_height
        return (1 - (y - self.origin_y) / self.height) * self.pixel_height

    @property
    def params(self) -> CanvasParams:
        """Get the full parameters object"""
        return self._params

    @property
    def width(self) -> int:
        """Get the logical width of the canvas"""
        return self._params.width

    @property
    def height(self) -> int:
        """Get the logical height of the canvas"""
        return self._params.height

    @property
    def rows(self) -> int:
        """Returns the number of active rows in the canvas."""
        if self.cols:
            return len(self.active_cells[0])
        else:
            return 0

    @property
    def cols(self) -> int:
        """Returns the number of active columns in the canvas."""
        return len(self.active_cells)

    @property
    def resolution(self) -> float:
        """Get the pixel resolution"""
        return self._params.resolution

    @property
    def origin_x(self) -> float:
        """Get the x-origin coordinate"""
        return self._params.origin_x

    @property
    def origin_y(self) -> float:
        """Get the y-origin coordinate"""
        return self._params.origin_y

    @property
    def xflip(self) -> bool:
        """Get the x-flip setting"""
        return self._params.xflip

    @property
    def yflip(self) -> bool:
        """Get the y-flip setting"""
        return self._params.yflip

    @property
    def xscale(self) -> Callable[[float], float]:
        """Get the x-scaling function"""
        return self._params.xscale

    @property
    def yscale(self) -> Callable[[float], float]:
        """Get the y-scaling function"""
        return self._params.yscale
