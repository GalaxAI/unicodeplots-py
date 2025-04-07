import base64
import io
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from PIL import Image
from PIL.Image import Image as PILImage


class Imageplot:
    """
    A class for creating plots with Unicode chars of images.
    Currently supports displaying images using the Kitty terminal protocol.
    """

    def __init__(
        self,
        *args,  # *Images (Paths, strs, or PIL.Image objects)
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

        self.dataset = self._parse_arguments(*args)
        self.images: List[str] = []

        self.plot()

    def _parse_arguments(self, *args) -> List[PILImage]:
        """
        Parse arguments provided during initialization.

        Args:
            *args: Arguments passed to __init__.

        Returns:
            A list of PIL.Image.Image objects.

        Raises:
            FileNotFoundError: If a path provided does not exist.
            ValueError: If an argument is not a str, Path, or PIL.Image.
            PIL.UnidentifiedImageError: If a file cannot be opened as an image.
        """
        dataset: List[PILImage] = []
        for value in args:
            img = None
            if isinstance(value, PILImage):
                img = value
            elif isinstance(value, (str, Path)):
                try:
                    path = Path(value).resolve()
                    if not path.is_file():
                        raise FileNotFoundError(f"Image file not found: {value}")
                    img = Image.open(path)
                except FileNotFoundError as e:
                    print(f"Error: {e}", file=sys.stderr)
                    continue  # Skip this value
                except Image.UnidentifiedImageError:
                    print(f"Error: Cannot identify image file format: {value}", file=sys.stderr)
                    continue  # Skip this value
                except Exception as e:  # Catch other potential PIL errors
                    print(f"Error opening image {value}: {e}", file=sys.stderr)
                    continue  # Skip this value
            else:
                print(f"Warning: Value needs to be a str, Path or PIL.Image. Ignoring value: {value!r}", file=sys.stderr)
                continue

            if img:
                dataset.append(img)
        return dataset

    def _display_kitty(self, image: PILImage) -> Tuple[int, int, str]:
        """
        Displays a single PIL Image using the Kitty terminal graphics protocol.

        Args:
            image: The PIL.Image.Image object to display.
        """

        # Convert image to PNG bytes in memory
        with io.BytesIO() as buf:
            save_format = "PNG"
            if image.mode == "RGBA" or "A" in image.mode:
                image.save(buf, format=save_format)
            else:
                image.save(buf, format=save_format)

            img_bytes = buf.getvalue()

        b64_img = base64.standard_b64encode(img_bytes)

        width, height = image.size

        kitty_sequence = f"\033_Gf=100,a=T,t=d,X=0,Y=0,C=1,s={width},v={height};{b64_img.decode('ascii')}\033\\  "
        return height, width, kitty_sequence

    def _image_to_unicode_str(self, image: PILImage) -> List[str]:
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
            new_height = self.img_h
            new_width = int(new_height / aspect_ratio * 2)  # Compensate for block aspect ratio

            resized = image.resize((new_width, new_height))
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

    def plot(self):
        """
        Plots the images in the dataset to the terminal.
        Currently uses the Kitty graphics protocol if detected.
        """
        term = os.environ.get("TERM", "")
        ascii_mode = os.environ.get("ASCII", "0") == "1"
        supported_terminal = ["xterm-kitty", "xterm-ghostty"]
        self.is_kitty = term in supported_terminal and not ascii_mode

        if not self.dataset:
            return

        if self.is_kitty:
            self.images = [self._display_kitty(img) for img in self.dataset]
        else:
            self.images = [self._image_to_unicode_str(img) for img in self.dataset]

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

        if not self.is_kitty:
            # Logic for unicode printing
            img_width = self.images[0][0].count("\x1b") // 2  # Adjustment to use whole terminal.
            max_images_per_row = max(1, term_width // (img_width + 5))
            for i in range(0, len(self.images), max_images_per_row):
                group = self.images[i : i + max_images_per_row]
                min_rows = min(len(img_str) for img_str in group)
                truncated_images = [img_str[:min_rows] for img_str in group]

                for row_parts in zip(*truncated_images):
                    print("|".join(row_parts))
        else:
            x_offset: int = 0
            # y_offset: int = 0
            for i, (height, width, img_data) in enumerate(self.images):
                img_data = img_data.replace("X=0", f"X={x_offset}")
                if i == len(self.images) - 1:
                    img_data = img_data.replace("C=1", "C=0")
                sys.stdout.write(img_data)
                x_offset += width

            print(x_offset)


if __name__ == "__main__":
    Imageplot("media/monarch.png", "galax.png").render()  # ,"galax.png","galax.png","galax.png","galax.png", 123, "non_existent_file.jpg").render()
