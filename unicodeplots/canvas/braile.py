from typing import Optional

from unicodeplots.canvas.canvas import Canvas
from unicodeplots.utils import CanvasParams, Color, ColorType


class BrailleCanvas(Canvas):
    @property
    def x_pixel_per_char(self) -> int:
        return 2

    @property
    def y_pixel_per_char(self) -> int:
        return 4

    _SUPERSAMPLE: int = 8

    def __init__(self, params: Optional[CanvasParams] = None, **kwargs):
        """
        Create a Braille-based canvas for unicode plotting.

        Args:
            params: Canvas parameters as a CanvasParams object
            **kwargs: Additional parameters that override values in params if provided
        """
        super().__init__(params=params, **kwargs)
        self.default_char = 0x2800
        self.active_cells = [[self.default_char] * self.grid_cols for _ in range(self.grid_rows)]

        self.default_color = Color.WHITE
        self.active_colors = [[self.default_color] * self.grid_cols for _ in range(self.grid_rows)]

        # Precompute bit values for faster pixel calculations
        self.bit_table = [
            [0x01, 0x02, 0x04, 0x40],  # x=0
            [0x08, 0x10, 0x20, 0x80],  # x=1
        ]

    def _set_pixel(self, px: int, py: int, color: ColorType) -> None:
        """Set a pixel in the Braille grid representation."""
        cx = px // self.x_pixel_per_char
        cy = py // self.y_pixel_per_char

        if not (0 <= cx < self.grid_cols and 0 <= cy < self.grid_rows):
            return

        try:
            x_in = px % self.x_pixel_per_char
            y_in = py % self.y_pixel_per_char
            bit = self.bit_table[x_in][y_in]
        except IndexError:
            return

        # Update cell bits
        self.active_cells[cy][cx] |= bit

        # Update color (simple overwrite)
        self.active_colors[cy][cx] = color

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
            self._set_pixel(p_x, p_y, color)

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
