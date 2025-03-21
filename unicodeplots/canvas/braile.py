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
        
        
        self.default_char = 0x2800
        self.active_cells = [
            [self.default_char] * self.grid_cols 
            for _ in range(self.grid_rows)
        ]
        
        self.default_color = Color.GREEN
        self.active_colors = [
            [self.default_color] * self.grid_cols 
            for _ in range(self.grid_rows)
        ]

        # Precompute bit values for faster pixel calculations
        self.bit_table = [
            [0x01, 0x02, 0x04, 0x40],   # x=0
            [0x08, 0x10, 0x20, 0x80],   # x=1
        ]
    
    def _set_pixel(self, px: int, py: int, color: ColorType, blend: bool):
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

    def render(self) -> str:
        """Efficient rendering with pre-allocated strings"""
        return '\n'.join(
            ''.join(
                ColorType(self.active_colors[row][col]).apply(chr(self.active_cells[row][col]))
                for col in range(self.grid_cols)
            )
            for row in range(self.grid_rows)
        )

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