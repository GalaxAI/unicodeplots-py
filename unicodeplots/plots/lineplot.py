from typing import List, Optional, Tuple, Union

from unicodeplots.canvas import BrailleCanvas
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
        title: Optional[str] = "",
        xlabel: Optional[str] = "",
        ylabel: Optional[str] = "",
        legend: Optional[bool] = False,
        show_border: Optional[bool] = None,
        border: Optional[str] = "single",
        **kwargs,
    ) -> None:
        """
        Initialize a line plot with data and styling parameters.

        Args:
            *args: Data to plot in various formats
            show_axes: Plots xy axis on the canvas.
            colors: Colors of plots
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            legend: Whether to show a legend
            show_border: Whether to show a border (auto-determined if None)
            border_style: Style of border to show ("single", "double", "bold", etc.)
            **kwargs: Styling parameters for canvas and box configuration
        """
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.legend = legend
        self.border_style = border

        # Determine whether to show border based on decorative elements
        self.show_border = show_border
        if show_border is None:
            self.show_border = bool(title or xlabel or ylabel or legend)

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

        # Case 3: x_range, *callables or other more complex combinations
        if len(args) >= 3 and isinstance(args[0], (list, tuple)) and len(args[0]) == 3:
            # Interpret first arg as (start, end, num_points)
            start, end, points = args[0]
            if not all(isinstance(v, (int, float)) for v in [start, end]):
                raise TypeError("Start and end values must be numbers")
            if not isinstance(points, int) or points <= 0:
                raise TypeError("Number of points must be a positive integer")

            x_data = [start + (end - start) * i / (points - 1) for i in range(points)]

            # Process each callable to create multiple datasets
            for func in args[1:]:
                if callable(func):
                    y_values = [func(x) for x in x_data]
                    # Validate and transform y values
                    y_data = []
                    for y in y_values:
                        if not isinstance(y, (int, float)):
                            raise TypeError(f"Function must return numeric values, got {type(y)}")
                        y_data.append(y_scale(y))

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
        return self.canvas.render()


if __name__ == "__main__":
    import math

    print("\n" + "=" * 60)
    print("EXAMPLE 1: Simple Linear Plot")
    print("=" * 60)
    print(Lineplot([1, 2, 7], [9, -6, 8]).render())
    print(Lineplot(list(range(-5, 5))).render())

    # Generate x values for trig functions
    x_vals = [x / 10 for x in range(-31, 62)]
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Trigonometric Functions")
    print("=" * 60)
    print("SIN Function:")
    print(Lineplot(x_vals, math.sin).render())

    print("\nCOS Function:")
    print(Lineplot(x_vals, math.cos).render())

    print("\nSIN + COS Together:")
    print(Lineplot(x_vals, math.sin, x_vals, math.cos).render())

    print("\n" + "=" * 60)
    print("EXAMPLE 3: Logarithmic Scale Comparison")
    print("=" * 60)
    # Generate data with exponential growth
    x_log = list(range(1, 11))
    y_log = [2**n for n in x_log]
    print("With Linear Scale:")
    print(Lineplot(x_log, y_log).render())

    print("\nWith Logarithmic Scale (log2):")
    print(Lineplot(x_log, y_log, yscale=lambda y: math.log2(y)).render())
    import math
    from pathlib import Path

    import torch

    save_path = Path("training_metrics.pt")
    metrics = torch.load(save_path)
    train_loss_per_step = metrics["train_loss_per_step"]
    train_acc_per_step = metrics["train_acc_per_step"]
    print(f"Loaded pre-saved metrics from {save_path.resolve()}")

    # Rest of the plotting code remains unchanged
    steps = list(range(len(train_loss_per_step)))

    print("\nTraining Loss (per step):")

    print(Lineplot(steps, train_loss_per_step).render())

    print("\nTraining Accuracy (per step):")
    print(Lineplot(steps, train_acc_per_step).render())
