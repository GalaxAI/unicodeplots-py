from typing import Dict, List, Optional, Tuple, Union

_BORDER_SETS = {
    "double": {
        "horizontal": "═",
        "vertical": "║",
        "top_left": "╔",
        "top_right": "╗",
        "bottom_left": "╚",
        "bottom_right": "╝",
        "left_t": "╠",
        "right_t": "╣",
        "top_t": "╦",
        "bottom_t": "╩",
        "cross": "╬",
    },
    "ascii": {
        "horizontal": "-",
        "vertical": "|",
        "top_left": "+",
        "top_right": "+",
        "bottom_left": "+",
        "bottom_right": "+",
        "left_t": "+",
        "right_t": "+",
        "top_t": "+",
        "bottom_t": "+",
        "cross": "+",
    },
    "single": {
        "horizontal": "─",
        "vertical": "│",
        "top_left": "┌",
        "top_right": "┐",
        "bottom_left": "└",
        "bottom_right": "┘",
        "left_t": "├",
        "right_t": "┤",
        "top_t": "┬",
        "bottom_t": "┴",
        "cross": "┼",
    },
    "none": {
        "horizontal": " ",
        "vertical": " ",
        "top_left": " ",
        "top_right": " ",
        "bottom_left": " ",
        "bottom_right": " ",
        "left_t": " ",
        "right_t": " ",
        "top_t": " ",
        "bottom_t": " ",
        "cross": " ",
    },
}

_DEFAULT_BORDER = _BORDER_SETS["none"]


def get_border_chars(border_type: str) -> Dict[str, str]:
    """
    Return characters for drawing borders based on type.

    Args:
        border_type: The style of the border ('single', 'double', 'ascii', 'none').

    Returns:
        A dictionary containing the characters for the specified border type.
        Returns space characters for unknown types or 'none'.
    """
    return _BORDER_SETS.get(border_type, _DEFAULT_BORDER)


class BorderBox:
    """A class that creates a box/border around a plot with title, axes, and labels."""

    _Y_LABEL_PADDING = 1  # Space between y-label and y-values
    _Y_VALUE_PADDING = 1  # Space between y-values and border
    _X_AXIS_PADDING = 1  # Space around content within the vertical borders
    _PLOT_AREA_HORIZONTAL_PADDING = _X_AXIS_PADDING * 2  # Total padding inside border

    def __init__(self, width: int, height: int, border_type: str = "single"):
        """
        Initialize the border box with dimensions.

        Args:
            width: Width of the plotting area in characters
            height: Height of the plotting area in characters
            border_type: Type of border ('single', 'double', 'ascii', or 'none')
        """
        self.width = width
        self.height = height
        self.title = ""
        self.x_label = ""
        self.y_label = ""
        self.x_range: Tuple[Union[int, float], Union[float, int]]
        self.y_range: Tuple[Union[int, float], Union[float, int]]
        self.border_chars = get_border_chars(border_type)
        # self.legend: Dict[str, str]

    def set_border_type(self, border_type: str) -> "BorderBox":
        """Set the border type and update border characters."""
        self.border_chars = get_border_chars(border_type)
        return self

    def set_title(self, title: str) -> "BorderBox":
        """Set the title of the plot."""
        self.title = title
        return self

    def set_x_label(self, label: str) -> "BorderBox":
        """Set the x-axis label."""
        self.x_label = label
        return self

    def set_y_label(self, label: str) -> "BorderBox":
        """Set the y-axis label."""
        self.y_label = label
        return self

    def set_ranges(self, x_range: Tuple[float, float], y_range: Tuple[float, float]) -> "BorderBox":
        """Set the x and y axis ranges."""
        if not (isinstance(x_range, tuple) and len(x_range) == 2 and isinstance(y_range, tuple) and len(y_range) == 2):
            raise ValueError("Ranges must be tuples of length 2 (min, max).")
        self.x_range = x_range
        self.y_range = y_range
        return self

    def set_width(self, width: int) -> "BorderBox":
        """Set the internal plot width."""
        if width < 1:
            raise ValueError("Width must be a positive integer.")
        self.width = width
        return self

    def set_height(self, height: int) -> "BorderBox":
        """Set the internal plot height."""
        if height < 1:
            raise ValueError("Height must be a positive integer.")
        self.height = height
        return self

    def _calculate_margins(self) -> Tuple[int, int, int]:
        """Calculate the left margin width based on y-label and y-axis values."""
        y_label_width = len(self.y_label) + self._Y_LABEL_PADDING if self.y_label else 0
        y_value_width = max(len(f"{self.y_range[0]:.1f}"), len(f"{self.y_range[1]:.1f}")) + 1
        left_margin = y_label_width + y_value_width
        return left_margin, y_label_width, y_value_width

    def _render_title(self, left_margin: int) -> str:
        """Render the title section of the plot."""
        top_border_inner_width = self.width + self._PLOT_AREA_HORIZONTAL_PADDING

        title_line = " " * left_margin + self.border_chars["top_left"]

        if self.title:
            # Calculate space needed for title
            title_with_spaces = f" {self.title} "

            remaining_width = top_border_inner_width - len(title_with_spaces)
            left_segment_len = remaining_width // 2
            right_segment_len = remaining_width - left_segment_len

            title_line += self.border_chars["horizontal"] * left_segment_len + title_with_spaces + self.border_chars["horizontal"] * right_segment_len
        else:
            # No title, just draw the horizontal line
            title_line += self.border_chars["horizontal"] * top_border_inner_width

        title_line += self.border_chars["top_right"]
        return title_line

    def _render_plot_content(self, plot_content: List[str], left_margin: int, y_label_width: int, y_value_width: int) -> List[str]:
        """Render the main plot content with y-axis labels and values."""
        result = []
        y_val_min, y_val_max = self.y_range
        y_val_max - y_val_min

        # Calculate y values for each row
        y_values = [self.y_range[1] - i * (self.y_range[1] - self.y_range[0]) / (self.height - 1) for i in range(self.height)]

        for i, line in enumerate(plot_content):
            # Construct the left margin part (label + value)
            # 1. Y-Label: Displayed vertically centered
            if i == self.height // 2 and self.y_label:
                y_label_part = " " + self.y_label
            else:
                y_label_part = " " * y_label_width

            # 2. Y-Value: Displayed at top and bottom rows

            if i == 0 or i == self.height - 1:
                # Only show values at top, middle, and bottom
                y_value = f"{y_values[i]:.1f}"
                y_value_part = y_value.rjust(y_value_width)
            else:
                y_value_part = " " * y_value_width

            plot_line = line.ljust(self.width)
            left_padding = " " * self._X_AXIS_PADDING
            # Padding inside the right border
            right_padding = " " * self._X_AXIS_PADDING

            result.append(f"{y_label_part}{y_value_part}{self.border_chars['vertical']}{left_padding}{plot_line}{right_padding}{self.border_chars['vertical']}")

        return result

    def _render_bottom_border(self, left_margin: int) -> str:
        """Render the bottom border line of the plot."""
        bottom_border_inner_width = self.width + self._PLOT_AREA_HORIZONTAL_PADDING
        return (
            " " * left_margin
            + self.border_chars["bottom_left"]
            + self.border_chars["horizontal"] * bottom_border_inner_width
            + self.border_chars["bottom_right"]
        )

    def _render_x_axis(self, left_margin: int) -> List[str]:
        """Render the x-axis with min and max values."""
        result = []
        min_str = f"{self.x_range[0]:.2f}"
        max_str = f"{self.x_range[1]:.2f}"

        x_values_line = " " * left_margin
        # Add min value at the beginning
        x_values_line += min_str

        # Add max value at the end, right-aligned
        content_width = self.width + self._PLOT_AREA_HORIZONTAL_PADDING
        spaces_needed = content_width - len(min_str) - len(max_str)
        x_values_line += " " * spaces_needed + max_str

        result.append(x_values_line)

        return result

    def _render_x_label(self, left_margin: int) -> Optional[str]:
        """Render the x-axis label."""
        if self.x_label:
            return " " * left_margin + " " + self.x_label.center(self.width)
        return None

    # def _render_legend(self, left_margin: int) -> List[str]:
    #     """Render the legend if it exists."""
    #     print("Not implemented yet.")
    #     return

    def render(self, plot_content: List[str]) -> List[str]:
        """
        Render the border box with the given plot content.

        Args:
            plot_content: A list of strings representing the plot to be framed

        Returns:
            A list of strings representing the complete framed plot
        """
        if len(plot_content) != self.height:
            raise ValueError(f"plot_content has {len(plot_content)} lines, expected {self.height}")

        # --- Calculation ---
        left_margin, y_label_width, y_value_width = self._calculate_margins()

        # --- Rendering Sections ---
        output_lines = []

        # 1. Title / Top Border
        output_lines.append(self._render_title(left_margin))

        # 2. Plot Content Area with Y-axis info and Side Borders
        output_lines.extend(self._render_plot_content(plot_content, left_margin, y_label_width, y_value_width))

        # 3. Bottom Border
        output_lines.append(self._render_bottom_border(left_margin))

        # 4. X-Axis Values
        output_lines.extend(self._render_x_axis(left_margin))

        # 5. X-Axis Label (Optional)
        x_label_line = self._render_x_label(left_margin)
        if x_label_line:
            output_lines.append(x_label_line)

        # 6. Legend (Optional)
        # output_lines.extend(self._render_legend(left_margin))

        return output_lines
