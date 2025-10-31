from random import random

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


class BetterImagePlot:
    """
    Takes only one image
    """

    def __init__(self, X: list[list[int]] | str | PILImage, img_h: int = 24, numeric: bool = True):
        self.X = X
        self.img_h = img_h
        self.numeric_mode = numeric
        ### Box params
        """
        I want to migrate box params somewhere
        """

    def render(self):
        self._parse_input()
        self.render_unicode(self.X)

    def unicode_encode(self, image) -> list[str]:
        rows = []
        is_rgb = len(image.shape) == 3

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

    def render_unicode(self, data):
        img = self.unicode_encode(data)
        for row in img:
            print(row)

    def _parse_input(self):
        match self.numeric_mode:
            case True:
                self.X = TensorAdapter(self.X)
            case False:
                # TODO reading file
                pass


if __name__ == "__main__":
    img = "media/monarch.png"

    ## Numeric
    grayscale = [[random() * 255 for _ in range(28)] for _ in range(28)]
    rgb = [[[random() * 255 for _ in range(3)] for _ in range(28)] for _ in range(28)]
    BetterImagePlot(rgb, img_h=24).render()
    BetterImagePlot(grayscale, img_h=24).render()
    ## Non numeric

    # BetterImagePlot(img, img_h=24).render()
