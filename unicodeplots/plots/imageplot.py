import base64
import io
import os
import sys
from pathlib import Path
from typing import List, Optional

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
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.legend = legend
        self.border_style = border  # Renamed to avoid conflict with border argument if used elsewhere

        self.dataset = self._parse_arguments(*args)
        # self.canvas = None  # No canvas implementation yet

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

    def _display_kitty(self, image: PILImage):
        """
        Displays a single PIL Image using the Kitty terminal graphics protocol.

        Args:
            image: The PIL.Image.Image object to display.
        """
        try:
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

            # Construct the Kitty protocol escape sequence
            # f=100: PNG format
            # a=T: Action = Transmit and display
            # t=d: Transmission = Direct (data follows)
            # s,v: Original image width and height in pixels
            # m=0: Indicates this is the last (or only) chunk of data
            kitty_sequence = f"\033_Gf=100,a=T,t=d,s={width},v={height},m=0;{b64_img.decode('ascii')}\033\\"

            sys.stdout.write(kitty_sequence)
            sys.stdout.flush()
            # Add a newline after the image for better separation in the terminal
            print()

        except Exception as e:
            print(f"Error displaying image with Kitty protocol: {e}", file=sys.stderr)
        finally:
            image.close()
            # Close the image object if it was opened from a file
            # Note: PIL might lazy-load, but explicit close is good practice
            # if we are sure we're done with it. Here, we might want to keep
            # it open if render() also needs it. Let's comment out close for now.
            # image.close() # Be careful if self.dataset is shared/reused
            pass

    def plot(self):
        """
        Plots the images in the dataset to the terminal.
        Currently uses the Kitty graphics protocol if detected.
        """
        term = os.environ.get("TERM", "")
        is_kitty = term.startswith("xterm-")

        if not self.dataset:
            print("No images loaded to display.", file=sys.stderr)
            return

        if is_kitty:
            print(f"Detected (TERM={term}). Using Kitty graphics protocol.")
            for img in self.dataset:
                self._display_kitty(img)
        else:
            print(f"Warning: Kitty terminal graphics protocol not detected (TERM={term}).", file=sys.stderr)
            print("Cannot display images directly in this terminal.", file=sys.stderr)
            # Future: Fallback to ASCII art or other methods here

    def render(self):
        """ """
        print("Render function not yet implemented.")
        pass  # For now, does nothing


if __name__ == "__main__":
    Imageplot("galax.png", 123, "non_existent_file.jpg")
