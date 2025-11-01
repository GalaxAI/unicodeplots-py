import base64
import os
import sys
from io import BytesIO
from pathlib import Path
from random import random
from typing import Sequence, TypeAlias

try:
    from PIL import Image
    from PIL.Image import Image as PILImage

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


from unicodeplots.utils import time_execution
from unicodeplots.utils.tensor import TensorAdapter

Image2D: TypeAlias = list[list[int]]
Image3D: TypeAlias = list[list[list[int]]]
strImage: TypeAlias = str | Path | PILImage


def pil_to_tensor(img: PILImage) -> list[list[list[int]]]:
    width, height = img.size
    pixels = list(img.getdata())

    # One-liner to reshape
    return [[[int(c) for c in pixels[y * width + x]] for x in range(width)] for y in range(height)]


def tensor_to_pil(data: TensorAdapter) -> Image:
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
    return img


class BetterImagePlot:
    """
    Takes only one image
    """

    def __init__(self, X: Image2D | Image3D | strImage, force_ascii=False):
        self.X = X
        self.pil_mode = (not force_ascii) and (os.environ.get("ASCII", "False") != "True") and PIL_AVAILABLE

    def render(self):
        tensor = self.parse_input()
        self.render_kitty(tensor) if self.pil_mode else self.render_unicode(tensor)

    def render_unicode(self, data: TensorAdapter):
        img = self.unicode_encode(data)
        for row in img:
            print(row)

    def render_kitty(self, data: PILImage):
        kitty_sequence = create_kitty_sequence(data)
        sys.stdout.write(kitty_sequence)

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

    def parse_input(self) -> TensorAdapter | PILImage:
        if isinstance(self.X, (str, PILImage, Path)):
            try:
                return load_image(self.X) if self.pil_mode else TensorAdapter(pil_to_tensor(load_image(self.X)))
            except Exception as e:
                print(f"Error loading image: {e}")
                # Load error image bc i think its funny
                raise ValueError("Error loading image")
        else:
            tensor = TensorAdapter(self.X)
            return tensor_to_pil(tensor) if self.pil_mode else tensor


def load_image(path: str | Path) -> PILImage:
    img = Image.open(path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


class GridImagePlot:
    def __init__(
        self,
        images: Sequence[Image2D | Image3D | strImage],
        *,
        cols: int = 5,
        padding: int = 16,
    ):
        if not images:
            raise ValueError("GridImagePlot requires at least one image.")
        self.images = list(images)
        self.cols = cols
        self.padding = max(0, padding)

    def render(self) -> None:
        pil_images = []
        for img in self.images:
            if isinstance(img, PILImage):
                pil_images.append(img)
            elif isinstance(img, (str, Path)):
                pil_images.append(load_image(img))
            else:  # Note this is really slow
                tensor = TensorAdapter(img)
                pil_images.append(tensor_to_pil(tensor))
        self.render_kittens(pil_images)

    def render_kittens(self, images: Sequence[PILImage]) -> None:
        x_offset = 0
        term_width = os.get_terminal_size().columns * 7
        rows, row = [], []
        for idx, img in enumerate(images):
            row.append(img)
            if x_offset + img.width >= term_width or len(row) >= self.cols:
                x_offset = 0
                rows.append(row)
                row = []
            else:
                x_offset += img.width + self.padding
        if row:
            rows.append(row)

        for row in rows:
            x_offset = 0
            for idx, img in enumerate(row):
                kitten = create_kitty_sequence(img)
                if idx == len(row) - 1:
                    kitten = kitten.replace("C=1", "C=0") + "\n"
                kitten = kitten.replace("X=0", f"X={x_offset}")
                x_offset += img.width + self.padding
                sys.stdout.write(kitten)
            sys.stdout.flush()


def create_kitty_sequence(img: PILImage) -> str:
    width, height = img.size
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_bytes = buffer.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
    kitty_sequence = f"\033_Gf=100,a=T,X=0,Y=0,C=1,s={width},v={height};{img_base64}\033\\"
    return kitty_sequence


@time_execution
def test_grid_strimages():
    img = "media/monarch.png"
    GridImagePlot([img] * 9, cols=3, padding=2).render()


@time_execution
def test_grid_mixed():
    img = "media/monarch.png"
    size = 256
    rgb = [[[random() * 255 for _ in range(3)] for _ in range(size)] for _ in range(size)]
    GridImagePlot([img, rgb, img, rgb, rgb], cols=3, padding=2).render()


@time_execution
def test_imageplot_str():
    img = "media/monarch.png"
    BetterImagePlot(img).render()


@time_execution
def test_imageplot_numeric():
    rgb = [[[random() * 255 for _ in range(3)] for _ in range(28)] for _ in range(28)]
    grayscale = [[random() * 255 for _ in range(28)] for _ in range(28)]

    BetterImagePlot(rgb).render()
    BetterImagePlot(grayscale).render()


if __name__ == "__main__":
    print(f"test_grid_strimages: {test_grid_strimages()}")
    print(f"test_grid_mixed: {test_grid_mixed()}")
    print(f"test_imageplot_str: {test_imageplot_str()}")
    print(f"test_imageplot_numeric: {test_imageplot_numeric()}")
