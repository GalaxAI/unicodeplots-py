import math
from abc import ABC, abstractmethod
from enum import IntEnum
from typing import Tuple, Optional, List, Callable

INVALID_COLOR = -1

class ColorType(IntEnum):
    """ANSI color codes with named constants and integer compatibility"""
    INVALID = INVALID_COLOR
    RED = 196
    GREEN = 46
    BLUE = 21
    WHITE = 15
    BLACK = 0
    ORANGE = 208
    YELLOW = 226
    PURPLE = 129

    @classmethod
    def _missing_(cls, value):
        """Allow creation from any integer while preserving enum benefits"""
        return cls.INVALID

    def ansi_prefix(self) -> str:
        """Generate ANSI escape code for the color"""
        if self == ColorType.INVALID:
            return ''
        return f"\033[38;5;{self.value}m"

    def apply(self, text: str) -> str:
        """Apply color to text with reset at end"""
        if self == ColorType.INVALID:
            return text
        return f"{self.ansi_prefix()}{text}\033[0m"

Color = ColorType

class Canvas(ABC):
    def __init__(self, 
            width: float,          # Logical width
            height: float,         # Logical height
            resolution: float = 1, # Pixels per logical unit
            origin_x: float = 0,
            origin_y: float = 0,
            xflip: bool = False,
            yflip: bool = False,
            blend: bool = True,
            xscale: Callable[[float], float] = lambda x: x,
            yscale: Callable[[float], float] = lambda y: y):
        
        self.width = width
        self.height = height
        self.resolution = resolution
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.xflip = xflip
        self.yflip = yflip
        self.blend = blend
        self.xscale = xscale
        self.yscale = yscale
        
        # Calculate pixel dimensions based on logical dimensions and resolution
        self.pixel_width = math.ceil(width * resolution)
        self.pixel_height = math.ceil(height * resolution)
        
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