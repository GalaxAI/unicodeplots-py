from dataclasses import fields
from typing import List, Tuple, Union

from unicodeplots.canvas import BrailleCanvas
from unicodeplots.utils import CanvasParams, Color


class Lineplot:
    """
    A class for creating line plots with Unicode characters.
    """

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize a line plot with data and styling parameters.

        Args:
            *args: Data to plot in various formats (see _parse_arguments)
            **kwargs: Styling parameters and canvas configuration
        """
        # Parse data from args first
        canvas_kwargs = self._extract_canvas_params(kwargs)
        self.canvas_params = CanvasParams(**canvas_kwargs)
        self.canvas = BrailleCanvas(self.canvas_params)

        self.other_kwargs = kwargs
        self.datasets = self._parse_arguments(*args)

        # Create canvas with validated parameters
        self.colors = kwargs.get("colors", [Color.GREEN, Color.RED, Color.BLUE, Color.YELLOW])
        self.auto_scale = kwargs.get("auto_scale", True)

        # Create canvas with extracted parameters
        self.plot()

    @staticmethod
    def _extract_canvas_params(all_kwargs: dict) -> dict:
        """Extract kwargs matching CanvasParams fields, return validated subset."""
        param_fields = {f.name for f in fields(CanvasParams)}
        return {k: v for k, v in all_kwargs.items() if k in param_fields}

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
            x_data = list(range(len(y_values)))
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

        # Compute data bounds for auto-scaling
        min_x, max_x, min_y, max_y = self._compute_data_bounds()

        # Update canvas parameters if auto_scale is enabled
        if self.auto_scale:
            # Set the origin point to match the data bounds
            self.canvas.params.origin_x = min_x
            self.canvas.params.origin_y = min_y

            # Update width and height to match data range
            self.canvas.params.width = max_x - min_x
            self.canvas.params.height = max_y - min_y

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
    print(Lineplot(list(range(10))).render())

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
