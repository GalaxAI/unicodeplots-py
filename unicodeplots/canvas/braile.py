from dataclasses import dataclass
from typing import List, Optional, Protocol, Union, runtime_checkable

from unicodeplots.canvas.canvas import Canvas
from unicodeplots.utils import CanvasParams, ColorType


@runtime_checkable
class PlotStyle(Protocol):
    def adjust_grid(self, canvas: "BrailleCanvas"):
        """Adjust the grid dimensions for the style."""
        ...

    def set_pixel(
        self,
        canvas: "BrailleCanvas",
        px: int,
        py: int,
        color: ColorType,
    ) -> None:
        """Style-specific logic for setting a pixel."""
        ...


@dataclass
class LineStyle:
    x_pixels: int = 2
    y_pixels: int = 4
    bit_table = [
        [0x01, 0x02, 0x04, 0x40],  # x=0
        [0x08, 0x10, 0x20, 0x80],  # x=1
    ]

    def adjust_grid(self, canvas: "Canvas") -> None:
        canvas._x_pixels = self.x_pixels
        canvas._y_pixels = self.y_pixels

    def set_pixel(
        self,
        canvas: "Canvas",
        px: int,
        py: int,
        color: ColorType,
        marker: Optional[Union[str, List[str]]] = None,
    ) -> None:
        cx = px // canvas.x_pixel_per_char
        cy = py // canvas.y_pixel_per_char

        if not (0 <= cx < canvas.grid_cols and 0 <= cy < canvas.grid_rows):
            return

        x_in = px % canvas.x_pixel_per_char
        y_in = py % canvas.y_pixel_per_char
        bit = self.bit_table[x_in][y_in]
        canvas.active_cells[cy][cx] |= bit
        canvas.active_colors[cy][cx] = color


@dataclass
class MarkerStyle:
    x_pixels = 1
    y_pixels = 1
    default_marker = "•"
    active_marker = default_marker

    def __init__(self, markers: Optional[Union[str, List[str]]] = None):
        if isinstance(markers, str):
            self.default_marker = markers
        elif isinstance(markers, list):
            self.markers = markers

    def set_marker(self, marker: str) -> "MarkerStyle":
        self.active_marker = marker
        return self

    def adjust_grid(self, canvas: "Canvas") -> None:
        canvas._x_pixels = self.x_pixels
        canvas._y_pixels = self.y_pixels

    def set_pixel(self, canvas: "Canvas", px: int, py: int, color: ColorType) -> None:
        cx = px // canvas.x_pixel_per_char
        cy = py // canvas.y_pixel_per_char

        if not (0 <= cx < canvas.grid_cols and 0 <= cy < canvas.grid_rows):
            return
        canvas.active_cells[cy][cx] = ord(self.active_marker)
        canvas.active_colors[cy][cx] = color


class BrailleCanvas(Canvas):
    _SUPERSAMPLE: int = 8

    def __init__(self, params: Optional[CanvasParams] = None, **kwargs):
        """
        Create a Braille-based canvas for unicode plotting.

        Args:
            params: Canvas parameters as a CanvasParams object
            **kwargs: Additional parameters that override values in params if provided
        """
        super().__init__(params=params, **kwargs)
        self.plot_style = self._init_plot_style(self.params.marker)
        self.plot_style.adjust_grid(self)

        self.active_cells = [[self.default_char] * self.grid_cols for _ in range(self.grid_rows)]
        self.active_colors = [[self.default_color] * self.grid_cols for _ in range(self.grid_rows)]

    def _init_plot_style(self, marker: Optional[Union[str, List[str]]]) -> PlotStyle:
        """Factory method to create the appropriate PlotStyle."""
        if marker:
            return MarkerStyle()
        else:
            return LineStyle()

    def _draw_bresenham_segment(self, px1: int, py1: int, px2: int, py2: int, color: ColorType):
        """Draws a single line segment using Bresenham given INTEGER pixel coordinates."""

        dx = abs(px2 - px1)
        dy = abs(py2 - py1)
        sx = 1 if px1 < px2 else -1
        sy = 1 if py1 < py2 else -1
        err = dx - dy

        pixels = set()
        px_curr, py_curr = px1, py1

        while True:
            pixels.add((px_curr // self._SUPERSAMPLE, py_curr // self._SUPERSAMPLE))

            if px_curr == px2 and py_curr == py2:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                px_curr += sx
            if e2 < dx:
                err += dx
                py_curr += sy

        # Set the actual pixels on the canvas
        for p_x, p_y in pixels:
            self.plot_style.set_pixel(self, p_x, p_y, color)

    def set_point(self, x: float, y: float, color: ColorType):
        """Set a point using PlotStyle."""
        px = self.x_to_pixel(x)
        py = self.y_to_pixel(y)
        self.plot_style.set_pixel(self, int(px), int(py), color)

    def line(self, x1: float, y1: float, x2: float, y2: float, color: ColorType):
        """Draw a line between logical coordinates using self._SUPERSAMPLEd Bresenham for smoother curves"""

        px1 = self.x_to_pixel(x1) * self._SUPERSAMPLE
        py1 = self.y_to_pixel(y1) * self._SUPERSAMPLE
        px2 = self.x_to_pixel(x2) * self._SUPERSAMPLE
        py2 = self.y_to_pixel(y2) * self._SUPERSAMPLE

        # Standard Bresenham at high resolution
        px1, py1 = int(round(px1)), int(round(py1))
        px2, py2 = int(round(px2)), int(round(py2))

        self._draw_bresenham_segment(px1, py1, px2, py2, color)

    def render(self) -> str:
        """Efficient rendering with pre-allocated strings"""
        return "\n".join(
            "".join(ColorType(self.active_colors[row][col]).apply(chr(self.active_cells[row][col])) for col in range(self.grid_cols))
            for row in range(self.grid_rows)
        )
