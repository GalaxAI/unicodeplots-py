from typing import List, Optional, Tuple, Union

from unicodeplots.canvas import BrailleCanvas
from unicodeplots.components import BorderBox
from unicodeplots.utils import Color, ColorType


class Lineplot:
    """
    A class for creating line plots with Unicode characters.
    """

    def __init__(
        self,
        *args,
        colors: Optional[Union[ColorType, List[ColorType]]] = None,
        show_axes: bool = False,
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        border: Optional[str] = "",
        legend: bool = False,
        **kwargs,
    ) -> None:
        """
        Initialize a line plot with data and styling parameters.

        Args:
            *args: Data to plot in various formats
            show_axes: Plots x & y axis on the canvas.
            colors: Colors of plots
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            legend: Whether to show a legend
            border: Style of border to show ("single", "double", "ascii", "none")
            **kwargs: Styling parameters for canvas and box configuration
        """
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.legend = legend
        self.border_style = border

        # Determine whether to show border based on decorative elements
        self.show_border = bool(title or xlabel or ylabel or legend or border)

        # Parse data from args first
        self.canvas = BrailleCanvas(**kwargs)
        self.datasets = self._parse_arguments(*args)
        self.min_x, self.max_x, self.min_y, self.max_y = self._compute_data_bounds()
        self.show_axes = show_axes
        self.colors = colors or [color for color in Color if color != Color.INVALID]
        self.auto_scale = kwargs.get("auto_scale", True)
        self.plot()

    def _parse_arguments(self, *args) -> List[Tuple[List[Union[float, int]], List[Union[float, int]]]]:
        """
        Parse arguments similar to matplotlib.pyplot.plot

        Supported formats:
        - y_data only: [1, 2, 3] (x will be range(len(y)))
        - x_data, y_data: [1, 2, 3], [4, 5, 6]
        - x_data, callable: [1, 2, 3], lambda x: x**2
        - x_range, *callables: (0, 10, 100), lambda x: x**2, lambda x: x**3

        Returns:
            List of (x_data, y_data) tuples
        """
        datasets: List[Tuple[List[Union[float, int]], List[Union[float, int]]]] = []
        y_scale = self.canvas.yscale
        x_data: List[Union[float, int]] = []
        y_data: List[Union[float, int]] = []
        if len(args) == 0:
            return datasets

        # Case 1: Single array/list - treat as y values
        if len(args) == 1:
            y_values = args[0]
            x_data = y_values
            # Apply y_scale transformation and validate data types
            for y in y_values:
                if not isinstance(y, (int, float)):
                    raise TypeError(f"Y values must be numbers, got {type(y)}")
                y_data.append(y_scale(y))

            # Type assertion for mypy
            datasets.append((
                x_data,  # type: ignore
                y_data,  # type: ignore
            ))
            return datasets

        # Case 2: x_data, y_data or x_data, callable
        if len(args) == 2:
            # Validate and convert x_data
            for x in args[0]:
                if isinstance(x, (int, float)):
                    x_data.append(x)
                else:
                    raise TypeError(f"X values must be numbers, got {type(x)}")

            # If second arg is callable, apply to x_data
            if callable(args[1]):
                y_values = [args[1](x) for x in x_data]
            else:
                y_values = args[1]

            # Apply y_scale transformation and validate data types
            for y in y_values:
                if isinstance(y, (int, float)):
                    y_data.append(y_scale(y))
                else:
                    raise TypeError(f"Y values must be numbers, got {type(y)}")

            # Type assertion for mypy
            datasets.append((
                x_data,  # type: ignore
                y_data,  # type: ignore
            ))
            return datasets

        # Process regular alternating x, y, x, y, ... arguments
        for i in range(0, len(args), 2):
            if i + 1 < len(args):
                x_data = []
                y_data = []
                # Validate and convert x_data
                for x in args[i]:
                    if not isinstance(x, (int, float)):
                        raise TypeError(f"X values must be numbers, got {type(x)}")
                    x_data.append(x)

                # If second arg is callable, apply to x_data
                if callable(args[i + 1]):
                    y_values = [args[i + 1](x) for x in x_data]
                else:
                    y_values = args[i + 1]

                # Validate and transform y values
                for y in y_values:
                    if not isinstance(y, (int, float)):
                        raise TypeError(f"Y values must be numbers, got {type(y)}")
                    y_data.append(y_scale(y))

                # Type assertion for mypy
                datasets.append((
                    x_data,  # type: ignore
                    y_data,  # type: ignore
                ))

        return datasets

    def _compute_data_bounds(self) -> tuple[float, float, float, float]:
        """
        Compute the min/max x and y values across all datasets.

        Returns:
            tuple: (min_x, max_x, min_y, max_y)
        """
        if not self.datasets:
            return (0.0, 1.0, 0.0, 1.0)

        # Initialize with the first point of the first dataset
        x_values = [x for dataset in self.datasets for x in dataset[0]]
        y_values = [y for dataset in self.datasets for y in dataset[1]]
        if not x_values or not y_values:
            return (0.0, 1.0, 0.0, 1.0)

        min_x = min(x_values)
        max_x = max(x_values)
        min_y = min(y_values)
        max_y = max(y_values)

        # Prevent division by zero if all values are the same
        if min_x == max_x:
            min_x -= 0.5
            max_x += 0.5
        if min_y == max_y:
            min_y -= 0.5
            max_y += 0.5

        return (min_x, max_x, min_y, max_y)

    def plot(self):
        """
        Draw the plot on the canvas.

        Returns:
            self: For method chaining
        """
        if not self.datasets:
            return self

        # Update canvas parameters if auto_scale is enabled
        if self.auto_scale:
            # Set the origin point to match the data bounds
            self.canvas.params.origin_x = self.min_x
            self.canvas.params.origin_y = self.min_y

            # Update width and height to match data range
            self.canvas.params.width = self.max_x - self.min_x
            self.canvas.params.height = self.max_y - self.min_y

        # add xy axis
        if self.show_axes:
            x_axis_y = max(0, self.min_y) if 0 >= self.min_y and 0 <= self.max_y else self.min_y
            self.canvas.line(self.min_x, x_axis_y, self.max_x, x_axis_y, color="WHITE")
            y_axis_x = max(0, self.min_x) if 0 >= self.min_x and 0 <= self.max_x else self.min_x
            self.canvas.line(y_axis_x, self.min_y, y_axis_x, self.max_y, color="WHITE")

        # Draw each dataset with its own color
        for idx, (x_data, y_data) in enumerate(self.datasets):
            color = self.colors[idx % len(self.colors)]

            for i in range(1, len(x_data)):
                # Draw the line segment - canvas will handle the scaling
                self.canvas.line(x_data[i - 1], y_data[i - 1], x_data[i], y_data[i], color=color)
        return self

    def render(self) -> str:
        """
        Render the canvas to screen or return as string.

        Returns:
            str: The string representation of the plot
        """
        raw_plot = self.canvas.render()

        # If no decorative elements are requested, return the raw plot
        if not self.show_border:
            return raw_plot

        plot_lines = raw_plot.splitlines()

        border_box = BorderBox(width=self.canvas.rows, height=self.canvas.cols, border_type=self.border_style or "")

        if self.title:
            border_box.set_title(self.title)

        if self.xlabel:
            border_box.set_x_label(self.xlabel)

        if self.ylabel:
            border_box.set_y_label(self.ylabel)

        border_box.set_ranges((self.min_x, self.max_x), (self.min_y, self.max_y))

        # Add legend items if requested
        if self.legend and hasattr(self, "legend_items"):
            print("Note: This is not implemented yet")

        framed_plot = border_box.render(plot_lines)
        return "\n".join(framed_plot)


if __name__ == "__main__":
    import math

    print(Lineplot([1, 2, 7], [9, -6, 8], show_border=True, title="EXAMPLE 1: Simple Linear Plot", xlabel="X", ylabel="Y").render())
    print(Lineplot(list(range(-5, 5)), show_border=True, title="EXAMPLE 1: Range Plot", border="double").render())

    # Generate x values for trig functions
    x_vals = [x / 10 for x in range(-31, 62)]

    print(Lineplot(x_vals, math.sin, show_border=True, title="EXAMPLE 2: Sine Function", xlabel="X", ylabel="sin(x)").render())

    print(Lineplot(x_vals, math.cos, show_border=True, title="EXAMPLE 2: Cosine Function", xlabel="X", ylabel="cos(x)", border="ascii").render())

    print(
        Lineplot(x_vals, math.sin, x_vals, math.cos, show_border=True, title="EXAMPLE 2: Trigonometric Functions", xlabel="X", ylabel="Y", legend=True).render()
    )

    # Generate data with exponential growth
    x_log = list(range(1, 11))
    y_log = [2**n for n in x_log]

    print(Lineplot(x_log, y_log, show_border=True, title="EXAMPLE 3: Exponential Growth (Linear Scale)", xlabel="X", ylabel="2^x").render())

    print(
        Lineplot(
            x_log,
            y_log,
            yscale=lambda y: math.log2(y),
            show_border=True,
            title="EXAMPLE 3: Exponential Growth (Log Scale)",
            xlabel="X",
            ylabel="log₂(2^x)",
            border="double",
        ).render()
    )

    from pathlib import Path

    from torch import load

    save_path = Path("training_metrics.pt")
    metrics = load(save_path)
    train_loss_per_step = metrics["train_loss_per_step"]
    train_acc_per_step = metrics["train_acc_per_step"]

    steps = list(range(1, len(train_loss_per_step) + 1))

    print(Lineplot(steps, train_loss_per_step, show_border=True, title="Training Loss", xlabel="Steps", ylabel="Loss").render())

    print(Lineplot(steps, train_acc_per_step, show_border=True, title="Training Accuracy", xlabel="Steps", ylabel="Accuracy").render())
