from typing import Dict, List, Optional, Tuple, Union


def get_border_chars(border_type: str) -> Dict[str, str]:
    """Return characters for drawing borders based on type"""
    if border_type == "double":
        return {
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
        }
    elif border_type == "ascii":
        return {
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
        }
    elif border_type == "single":
        return {
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
        }
    else:  # No border
        return {
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
        }


class BorderBox:
    """A class that creates a box/border around a plot with title, axes, and labels."""

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
        self.legend: Dict[str, str]
        self.border_chars = get_border_chars(border_type)

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
        self.x_range = x_range
        self.y_range = y_range
        return self

    def add_legend_item(self, key: str, description: str) -> "BorderBox":
        """Add an item to the legend."""
        self.legend[key] = description
        return self

    def set_width(self, width: int) -> "BorderBox":
        self.width = width
        return self

    def set_height(self, height: int) -> "BorderBox":
        self.height = height
        return self

    def _calculate_margins(self) -> Tuple[int, int, int]:
        """Calculate the left margin width based on y-label and y-axis values."""
        y_label_width = len(self.y_label) + 1 if self.y_label else 0
        y_value_width = max(len(f"{self.y_range[0]:.1f}"), len(f"{self.y_range[1]:.1f}")) + 1
        left_margin = y_label_width + y_value_width
        return left_margin, y_label_width, y_value_width

    def _render_title(self, left_margin: int) -> str:
        """Render the title section of the plot."""
        if self.title:
            # Calculate space needed for title
            title_with_spaces = f" {self.title} "  # Title with spaces on both sides
            available_width = self.width + 2 - len(title_with_spaces)  # Total width minus title width

            left_segment = available_width // 2
            right_segment = available_width - left_segment  # Handle odd lengths correctly

            # Create the top border with title between two box segments
            return (
                " " * left_margin
                + self.border_chars["top_left"]
                + self.border_chars["horizontal"] * left_segment
                + title_with_spaces
                + self.border_chars["horizontal"] * right_segment
                + self.border_chars["top_right"]
            )
        else:
            # No title, so just create a simple top border
            return " " * left_margin + self.border_chars["top_left"] + self.border_chars["horizontal"] * (self.width + 2) + self.border_chars["top_right"]

    def _render_plot_content(self, plot_content: List[str], left_margin: int, y_label_width: int, y_value_width: int) -> List[str]:
        """Render the main plot content with y-axis labels and values."""
        result = []

        # Calculate y values for each row
        y_values = [self.y_range[1] - i * (self.y_range[1] - self.y_range[0]) / (self.height - 1) for i in range(self.height)]

        for i, line in enumerate(plot_content):
            # Add y-label for the middle line
            if i == self.height // 2 and self.y_label:
                y_label_part = " " + self.y_label
            else:
                y_label_part = " " * y_label_width

            # Add y-value for this line
            if i == 0 or i == self.height - 1:
                # Only show values at top, middle, and bottom
                y_value = f"{y_values[i]:.1f}"
                y_value_part = y_value.rjust(y_value_width)
            else:
                y_value_part = " " * y_value_width

            plot_line = line.ljust(self.width)

            result.append(f"{y_label_part}{y_value_part}{self.border_chars['vertical']} {plot_line} {self.border_chars['vertical']}")

        return result

    def _render_bottom_border(self, left_margin: int) -> str:
        """Render the bottom border of the plot."""
        return " " * left_margin + self.border_chars["bottom_left"] + self.border_chars["horizontal"] * (self.width + 2) + self.border_chars["bottom_right"]

    def _render_x_axis(self, left_margin: int) -> List[str]:
        """Render the x-axis with min and max values."""
        result = []

        # Format min and max values
        min_value = f"{self.x_range[0]:.2f}"
        max_value = f"{self.x_range[1]:.2f}"

        x_values_line = " " * left_margin
        # Add min value at the beginning
        x_values_line += min_value

        # Add max value at the end, right-aligned
        spaces_needed = self.width - len(min_value) - len(max_value) + 2
        x_values_line += " " * spaces_needed + max_value

        result.append(x_values_line)

        return result

    def _render_x_label(self, left_margin: int) -> Optional[str]:
        """Render the x-axis label."""
        if self.x_label:
            return " " * left_margin + " " + self.x_label.center(self.width)
        return None

    def _render_legend(self, left_margin: int) -> List[str]:
        """Render the legend if it exists."""
        result = []

        if self.legend:
            result.append("")  # Add a blank line
            result.append(" " * left_margin + "Legend:")

            for key, description in self.legend.items():
                result.append(" " * left_margin + f"{key} - {description}")

        return result

    def render(self, plot_content: List[str]) -> List[str]:
        """
        Render the border box with the given plot content.

        Args:
            plot_content: A list of strings representing the plot to be framed

        Returns:
            A list of strings representing the complete framed plot
        """
        result = []

        # Calculate margins
        left_margin, y_label_width, y_value_width = self._calculate_margins()

        # Render title section
        result.append(self._render_title(left_margin))

        # Render plot content with y-axis
        result.extend(self._render_plot_content(plot_content, left_margin, y_label_width, y_value_width))

        # Render bottom border
        result.append(self._render_bottom_border(left_margin))

        # Render x-axis
        result.extend(self._render_x_axis(left_margin))

        # Render x-axis label
        x_label = self._render_x_label(left_margin)
        if x_label:
            result.append(x_label)

        # Render legend
        # result.extend(self._render_legend(left_margin))

        return result
