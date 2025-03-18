from abc import ABC, abstractmethod
from typing import Callable
import math

from unicodeplots.utils import CanvasParams, ColorType


class Canvas(ABC):
    def __init__(self,
        params: CanvasParams = None, **kwargs):

        if params is None:
            params = CanvasParams()

        for key, value in kwargs.items():
            if hasattr(params, key):
                setattr(params, key, value)

        # Store params
        self._params = params

        # Calculate pixel dimensions based on logical dimensions and resolution
        self.pixel_width = math.ceil(params.width * params.resolution)
        self.pixel_height = math.ceil(params.height * params.resolution)

        # Ensure pixel dimensions are multiples of character cell dimensions
        self.pixel_width = self._align_to_char_width(self.pixel_width)
        self.pixel_height = self._align_to_char_height(self.pixel_height)

    def _align_to_char_width(self, width: int) -> int:
        """Ensure width is aligned to character cell boundaries"""
        remainder = width % self.x_pixel_per_char
        if remainder > 0:
            return width + (self.x_pixel_per_char - remainder)
        return width

    def _align_to_char_height(self, height: int) -> int:
        """Ensure height is aligned to character cell boundaries"""
        remainder = height % self.y_pixel_per_char
        if remainder > 0:
            return height + (self.y_pixel_per_char - remainder)
        return height

    @property
    @abstractmethod
    def x_pixel_per_char(self) -> int:
        pass

    @property
    @abstractmethod
    def y_pixel_per_char(self) -> int:
        pass

    @abstractmethod
    def _set_pixel(self, px: int, py: int, color: ColorType, blend: bool):
        pass

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
    def blend(self) -> bool:
        """Get the color blending setting"""
        return self._params.blend

    @property
    def xscale(self) -> Callable[[float], float]:
        """Get the x-scaling function"""
        return self._params.xscale

    @property
    def yscale(self) -> Callable[[float], float]:
        """Get the y-scaling function"""
        return self._params.yscale

    def x_to_pixel(self, x: float) -> float:
        """Convert logical x coordinate to pixel space"""
        scaled = self.xscale(x)
        if self.xflip:
            return (1 - (scaled - self.origin_x) / self.width) * self.pixel_width
        return ((scaled - self.origin_x) / self.width) * self.pixel_width

    def y_to_pixel(self, y: float) -> float:
        """Convert logical y coordinate to pixel space"""
        scaled = self.yscale(y)
        if self.yflip:
            return (scaled - self.origin_y) / self.height * self.pixel_height
        return (1 - (scaled - self.origin_y) / self.height) * self.pixel_height

    def pixel(self, x: float, y: float, color: ColorType, blend: bool = None):
        """Set a pixel at logical coordinates (x,y)"""
        if blend is None:
            blend = self.blend
        px = math.floor(self.x_to_pixel(x))
        py = math.floor(self.y_to_pixel(y))
        if 0 <= px < self.pixel_width and 0 <= py < self.pixel_height:
            self._set_pixel(px, py, color, blend)

    def line(self, x1: float, y1: float, x2: float, y2: float, color: ColorType, blend: bool = None):
        """Draw a line between logical coordinates (x1,y1) and (x2,y2)"""
        if blend is None:
            blend = self.blend
        px1 = self.x_to_pixel(x1)
        py1 = self.y_to_pixel(y1)
        px2 = self.x_to_pixel(x2)
        py2 = self.y_to_pixel(y2)

        dx = px2 - px1
        dy = py2 - py1
        steps = int(max(abs(dx), abs(dy)))
        if steps == 0:
            return

        x_inc = dx / steps
        y_inc = dy / steps

        for i in range(steps + 1):
            x = px1 + i * x_inc
            y = py1 + i * y_inc
            self._set_pixel(math.floor(x), math.floor(y), color, blend)

    def render(self) -> str:
        lines = []
        for row_idx in range(self.grid_rows):
            line = []
            for col_idx in range(self.grid_cols):
                char = self.grid[row_idx][col_idx]
                color = self.colors[row_idx][col_idx]
                line.append(ColorType(color).apply(char))
            lines.append(''.join(line))
        return '\n'.join(lines)