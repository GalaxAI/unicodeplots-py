import base64
import io
import os
import sys
from pathlib import Path
from typing import List, Literal, Optional, Sequence, Tuple, TypeAlias, Union

from PIL import Image
from PIL.Image import Image as PILImage

# Type aliases for different data types
NumericData: TypeAlias = List[List[Union[int, float, Sequence[Union[int, float]]]]]

SUPPORTED_TERM = ["xterm-kitty", "xterm-ghostty"]


class Imageplot:
    """
    A class for creating plots with Unicode chars of images.
    Currently supports displaying images using the Kitty terminal protocol.
    """

    def __init__(
        self,
        *args,  # *Images (Paths, strs, or PIL.Image objects)
        # Also I want to add support for numpy arrays, pytorch tensors, and tinygrad tensors
        img_h: int = 24,
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        border: Optional[str] = "",
        legend: bool = False,
        **kwrags,  # Keep kwargs for potential future canvas options
    ):
        """
        Initializes the Imageplot object.

        Args:
            *args: Variable number of image sources. Can be file paths (str or Path)
                   or pre-loaded PIL.Image objects.
            title: Optional title for the plot area (currently unused for direct display).
            xlabel: Optional label for the x-axis (currently unused for direct display).
            ylabel: Optional label for the y-axis (currently unused for direct display).
            border: Optional border style (currently unused for direct display).
            legend: Whether to display a legend (currently unused for direct display).
            **kwargs: Additional keyword arguments (reserved for future use, e.g., canvas options).
        """
        self.img_h = img_h
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.legend = legend
        self.border_style = border

        self.mode: Literal["numeric", "image"] = "image"
        self.dataset = self._parse_arguments(*args)
        self.images: List[Tuple[int, int, str]] | List[List[str]] = []

        self.plot()

    def _match_value(self, value) -> Union[PILImage, None]:
        match value:
            case PILImage():
                return value
            case str() | Path():
                try:  # Attempt to open the image
                    path = Path(value).resolve()
                    if not path.is_file():
                        raise FileNotFoundError(f"Image file not found: {value}")
                    return Image.open(path)
                except FileNotFoundError as e:
                    print(f"Error: {e}", file=sys.stderr)
                except Image.UnidentifiedImageError:
                    print(f"Error: Cannot identify image file format: {value}", file=sys.stderr)
                except Exception as e:  # Catch other potential PIL errors
                    print(f"Error opening image {value}: {e}", file=sys.stderr)
            case list() | tuple():
                if self.mode == "numeric":
                    # Convert tuples to lists for consistent typing
                    return self._matrix_to_pil(list(value))
                else:
                    # This will return List[PILImage] since mode isn't numeric
                    return [self._match_value(item) for item in value]  # type: ignore
            case _:
                return None
        return None

    def _parse_arguments(self, *args) -> List[PILImage]:
        """
        Parse arguments provided during initialization.

        Args:
            *args: Arguments passed to __init__. Each argument can be:
                - A string or Path object representing a path to an image file
                - A PIL.Image.Image object
                - An iterable containing any of the above types

        Returns:
            A list of PIL.Image.Image objects or NumericData.

        Raises:
            FileNotFoundError: If a path provided does not exist.
            ValueError: If an argument is not a str, Path, PIL.Image, or an iterable of these.
            PIL.UnidentifiedImageError: If a file cannot be opened as an image.
        """
        parsed_data: List[PILImage] = []

        has_str = any(isinstance(arg, (str, Path, PILImage)) for arg in args)
        has_numeric = any(isinstance(arg, (tuple, list, set)) for arg in args)
        if has_str and has_numeric:
            raise TypeError("Iterable cannot contain str and tuple at the same time")
        self.mode = "numeric" if has_numeric else "image"

        for value in args:
            img = self._match_value(value)
            if img is not None:
                parsed_data.append(img)

        return parsed_data

    def _img_to_kitty_str(self, image: PILImage) -> Tuple[int, int, str]:
        """
        Displays a single PIL Image using the Kitty terminal graphics protocol.

        Args:
            image: The PIL.Image.Image object to display.
        """

        # Convert image to PNG bytes in memory
        with io.BytesIO() as buf:
            save_format = "PNG"
            image.save(buf, format=save_format)
            img_bytes = buf.getvalue()

        b64_img = base64.standard_b64encode(img_bytes)
        decoded = b64_img.decode("ascii")
        width, height = image.size

        # NOTE: https://sw.kovidgoyal.net/kitty/graphics-protocol/#control-data-reference
        kitty_sequence = f"\033_Gf=100,a=T,t=d,X=0,Y=0,C=1,s={width},v={height};{decoded}\033\\  "
        return height, width, kitty_sequence

    def _img_to_unicode_str(self, image: PILImage) -> List[str]:
        """
        Converts an image to a list of strings (one per row) using Unicode blocks.

        Args:
            image: PIL Image to convert.

        Returns:
            List of strings, where each string represents a row of the image.
        """
        try:
            original_width, original_height = image.size
            aspect_ratio = original_height / original_width
            new_width = int(self.img_h / aspect_ratio * 2)  # Compensate for block aspect ratio

            resized = image.resize((new_width, self.img_h))
            if resized.mode != "RGB":
                resized = resized.convert("RGB")

            pixels = resized.load()
            width, height = resized.size
            rows = []

            for y in range(height):
                row_str = ""
                for x in range(width):
                    r, g, b = pixels[x, y]  # type: ignore
                    row_str += f"\033[48;2;{r};{g};{b}m \033[0m"
                rows.append((row_str))
            return rows

        except Exception as e:
            print(f"Error converting image to Unicode string: {e}", file=sys.stderr)
            return []

    def _matrix_to_pil(self, matrix: NumericData) -> PILImage:
        """
        Converts a 2D and 3D matrix to a PIL Image.
        Args:
            matrix: A 2D or 3D list representing pixel values.
        Returns:
            A PIL Image object.
        """

        height = len(matrix)
        width = len(matrix[0]) if height > 0 else 0

        # Determine if data is grayscale or RGB by checking structure
        dim = 1
        if height > 0 and width > 0 and isinstance(matrix[0][0], (list, tuple)):
            dim = len(matrix[0][0])

        pilImg = Image.new("L" if dim == 1 else "RGB", (width, height))
        pilImg.putdata([p if isinstance(p, (int, float)) else tuple(p) for row in matrix for p in row])  # type: ignore
        return pilImg

    def plot(self):
        """
        Plots the images in the dataset to the terminal.
        Currently uses the Kitty graphics protocol if detected.
        """
        term = os.environ.get("TERM", "")
        ascii_mode = os.environ.get("ASCII", "0") == "1"
        self.is_kitty = term in SUPPORTED_TERM and not ascii_mode

        if not self.dataset:
            return

        if self.is_kitty:
            self.images = [self._img_to_kitty_str(img) for img in self.dataset]
        else:
            self.images = [self._img_to_unicode_str(img) for img in self.dataset]

    def render(self):
        """
        Renders the pre-processed images horizontally.
        """
        if not self.images:
            return
        try:
            term_width = os.get_terminal_size().columns
        except (AttributeError, OSError):
            term_width = 120  # Fallback width

        if self.is_kitty:
            # NOTE: we are assuming 10pt font and but to keep it safe we are keeping a safe place
            x_offset: int = 0
            font_size = 10 / 1.5
            max_width = term_width * font_size

            # Pre-processing
            images = []
            row = []
            for i, (height, width, img_data) in enumerate(self.images):
                if x_offset + width >= max_width:
                    # last value
                    img_data = img_data.replace("C=1", "C=0") + "\n"
                    row.append([height, width, img_data])
                    images.append(row)
                    row = []
                    x_offset = 0
                else:
                    row.append([height, width, img_data])
                    x_offset += width

            # Ensure the last element in the final row also has C=0
            if row:
                last_height, last_width, last_img_data = row[-1]
                row[-1] = [last_height, last_width, last_img_data.replace("C=1", "C=0") + "\n"]
                images.append(row)

            for row in images:
                x_offset = 0
                for height, width, img_data in row:
                    img_data = img_data.replace("X=0", f"X={x_offset}")
                    sys.stdout.write(img_data)
                    x_offset += width
                x_offset = 0
                sys.stdout.flush()
            print("\n\n")

        else:
            # Logic for unicode printing
            img_width = self.images[0][0].count("\x1b") // 2  # Adjustment to use whole terminal.
            max_images_per_row = max(1, term_width // (img_width + 5))
            for i in range(0, len(self.images), max_images_per_row):
                print()
                group = self.images[i : i + max_images_per_row]
                min_rows = min(len(img_str) for img_str in group)
                truncated_images = [img_str[:min_rows] for img_str in group]

                for row_parts in zip(*truncated_images):
                    print(" | ".join(row_parts))


if __name__ == "__main__":
    # TODO THIS IS WIP
    import random

    img = "/home/billy/Programming/unicodeplot-py/media/monarch.png"
    Imageplot(img).render()
    Imageplot(img, img, img).render()

    # Create a 28x28 grayscale image with nested lists
    size = 128
    grayscale = [[random.randint(0, 255) for _ in range(size)] for _ in range(size)]
    # Create a 28x28 RGB image with nested lists
    rgb = [[[random.randint(0, 255) for _ in range(3)] for _ in range(size)] for _ in range(size)]

    Imageplot(grayscale).render()
    Imageplot(rgb).render()
    Imageplot(grayscale, rgb).render()
