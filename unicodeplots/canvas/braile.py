from unicodeplots.canvas.canvas import Canvas
from unicodeplots.utils import INVALID_COLOR, CanvasParams, Color, ColorType


class BrailleCanvas(Canvas):
    @property
    def x_pixel_per_char(self) -> int:
        return 2

    @property
    def y_pixel_per_char(self) -> int:
        return 4

    def __init__(self, params: CanvasParams = None, **kwargs):
        """
        Create a Braille-based canvas for unicode plotting.

        Args:
            params: Canvas parameters as a CanvasParams object
            **kwargs: Additional parameters that override values in params if provided
        """
        super().__init__(params=params, **kwargs)

        self.grid_rows = self.pixel_height // self.y_pixel_per_char
        self.grid_cols = self.pixel_width // self.x_pixel_per_char
        self.grid = [[chr(0x2800) for _ in range(self.grid_cols)]
                    for _ in range(self.grid_rows)]
        self.colors = [[INVALID_COLOR for _ in range(self.grid_cols)]
                      for _ in range(self.grid_rows)]

    def _set_pixel(self, px: int, py: int, color: ColorType, blend: bool):
        cx = px // self.x_pixel_per_char
        cy = py // self.y_pixel_per_char
        if not (0 <= cx < self.grid_cols and 0 <= cy < self.grid_rows):
            return

        x_in = px % self.x_pixel_per_char
        y_in = py % self.y_pixel_per_char

        # Braille bit mapping
        bit = 0
        if x_in == 0:
            if y_in == 0: bit = 0x01
            elif y_in == 1: bit = 0x02
            elif y_in == 2: bit = 0x04
            elif y_in == 3: bit = 0x40
        else:
            if y_in == 0: bit = 0x08
            elif y_in == 1: bit = 0x10
            elif y_in == 2: bit = 0x20
            elif y_in == 3: bit = 0x80

        # Update Braille character
        current = ord(self.grid[cy][cx]) - 0x2800
        self.grid[cy][cx] = chr(0x2800 + (current | bit))

        # Update color (simplified)
        current_color = self.colors[cy][cx]
        if current_color == INVALID_COLOR or not blend:
            self.colors[cy][cx] = color
        else:
            self.colors[cy][cx] = color  # Simple overwrite for demo


# Demo Script
if __name__ == "__main__":
    # Create canvas with logical dimensions 32x16 and resolution 2
    canvas = BrailleCanvas(
        width=32,
        height=16,
        resolution=4,
        origin_x=0,
        origin_y=0,
        xflip=False,
        yflip=False,
        blend=False
    )

    # Draw diagonal lines - no need to manually scale coordinates
    points = [
        (0, 16),
        (5, 0),
        (32, 16)
    ]

    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i+1]
        print(f"Drawing line from {(x1, y1)} to {(x2, y2)}")
        canvas.line(x1, y1, x2, y2, color=Color.BLUE)
    b = [
        (0,0),
        (5,5),
        (32,10)
    ]
    for i in range(len(b) - 1):
        x1, y1 = b[i]
        x2, y2 = b[i+1]
        print(f"Drawing line from {(x1, y1)} to {(x2, y2)}")
        canvas.line(x1, y1, x2, y2, color=Color.RED)

    print(canvas.render())