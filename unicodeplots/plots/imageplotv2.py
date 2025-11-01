import base64
import sys
from io import BytesIO
from pathlib import Path
from random import random
from typing import TypeAlias

from PIL import Image
from PIL.Image import Image as PILImage

from unicodeplots.utils.tensor import TensorAdapter

### X
"""
X could be :
    # Numeric
    Array of 2D image
    Array of 3D image
    # Not numeric
    PIL.Image.Image
    str ~ path
"""

Image2D: TypeAlias = PILImage | list[list[int]] | str
Image3D: TypeAlias = list[list[list[int]]] | str | PILImage


class BetterImagePlot:
    """
    Takes only one image
    """

    def __init__(self, X: Image2D | Image3D):
        self.X = X
        ### Box params
        """
        I want to migrate box params somewhere
        """

    def render(self):
        self._parse_input()
        self.render_kitty(self.X)
        self.render_unicode(self.X)

    def render_kitty(self, data):
        shape = data.shape
        mode = "RGB" if len(shape) == 3 and shape[2] == 3 else "L"
        height, width = shape[0], shape[1]
        flat_pixels = []
        for row in data:
            for pixel in row:
                pixel = tuple(map(int, pixel)) if mode == "RGB" else int(pixel)
                flat_pixels.append(pixel)

        img = Image.new(mode, size=(width, height))
        img.putdata(data=flat_pixels)

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")
        kitty_sequence = f"\033_Gf=100,a=T,t=d,X=0,Y=0,C=0,s={width},v={height};{img_base64}\033\\  \n"
        sys.stdout.write(kitty_sequence)

    def render_unicode(self, data):
        img = self.unicode_encode(data)
        for row in img:
            print(row)

    def unicode_encode(self, image: TensorAdapter) -> list[str]:
        rows = []
        is_rgb = len(image.shape) == 3 and image.shape[2] == 3

        for y in range(image.shape[0]):
            row = ""
            for x in range(image.shape[1]):
                if is_rgb:
                    r, g, b = list(map(int, image[y, x]))
                    row += f"\033[48;2;{r};{g};{b}m \033[0m"
                else:
                    p = int(image[y, x])
                    row += f"\033[48;2;{p};{p};{p}m \033[0m"
            rows.append(row)
        return rows

    @staticmethod
    def load_image(path: str | Path) -> list[list[list[int]]]:
        img = Image.open(path)

        if img.mode != "RGB":
            img = img.convert("RGB")

        width, height = img.size
        pixels = list(img.getdata())

        # One-liner to reshape
        return [[[int(c) for c in pixels[y * width + x]] for x in range(width)] for y in range(height)]

    def _parse_input(self):
        # Add ensure Int
        match isinstance(self.X, (str, PILImage, Path)):
            case True:
                try:
                    self.X = TensorAdapter(self.load_image(self.X))
                except Exception as e:
                    print(f"Error loading image: {e}")
                    # Load error image bc i think its funny
                pass
            case False:  # Numeric
                self.X = TensorAdapter(self.X)


if __name__ == "__main__":
    img = "media/monarch.png"

    ## Numeric
    rgb = [[[random() * 255 for _ in range(3)] for _ in range(28)] for _ in range(28)]
    grayscale = [[random() * 255 for _ in range(28)] for _ in range(28)]
    BetterImagePlot(rgb).render()
    BetterImagePlot(grayscale).render()
    ## Non numeric

    # BetterImagePlot(img).render()
