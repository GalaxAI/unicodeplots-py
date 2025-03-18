from typing import List, Tuple, Callable, Any, Optional, Union
from dataclasses import fields

from unicodeplots.canvas import BrailleCanvas
from unicodeplots.utils import Color, CanvasParams

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
        self.colors = kwargs.get('colors', [Color.GREEN, Color.RED, Color.BLUE, Color.YELLOW])
        self.auto_scale = kwargs.get('auto_scale', True)

        # Create canvas with extracted parameters
        self.plot()

    @staticmethod
    def _extract_canvas_params(all_kwargs: dict) -> dict:
        """Extract kwargs matching CanvasParams fields, return validated subset."""
        param_fields = {f.name for f in fields(CanvasParams)}
        return {k: v for k, v in all_kwargs.items() if k in param_fields}

    def _parse_arguments(self, *args) -> List[Tuple[List[float], List[float]]]:
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
        datasets = []
        y_scale = self.other_kwargs.get('y_scale', lambda x: x)

        if len(args) == 0:
            return datasets

        # Case 1: Single array/list - treat as y values
        if len(args) == 1:
            y_data = args[0]
            x_data = list(range(len(y_data)))
            # Apply y_scale transformation
            y_data = [y_scale(y) for y in y_data]
            datasets.append((x_data, y_data))
            return datasets

        # Case 2: x_data, y_data or x_data, callable
        if len(args) == 2:
            x_data = args[0]

            # If second arg is callable, apply to x_data
            if callable(args[1]):
                y_data = [args[1](x) for x in x_data]
            else:
                y_data = args[1]
                
            # Apply y_scale transformation
            y_data = [y_scale(y) for y in y_data]
            datasets.append((x_data, y_data))
            return datasets

        # Case 3: x_range, *callables or other more complex combinations
        if len(args) >= 3 and isinstance(args[0], (list, tuple)) and len(args[0]) == 3:
            # Interpret first arg as (start, end, num_points)
            start, end, points = args[0]
            x_data = [start + (end - start) * i / (points - 1) for i in range(points)]

            # Process each callable to create multiple datasets
            for func in args[1:]:
                if callable(func):
                    y_data = [func(x) for x in x_data]
                    datasets.append((x_data, y_data))

            return datasets

        # Process regular alternating x, y, x, y, ... arguments
        for i in range(0, len(args), 2):
            if i + 1 < len(args):
                x_data = args[i]
                # If second arg is callable, apply to x_data
                if callable(args[i + 1]):
                    y_data = [args[i + 1](x) for x in x_data]
                else:
                    y_data = args[i + 1]
                datasets.append((x_data, y_data))

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
                self.canvas.line(x_data[i-1], y_data[i-1], x_data[i], y_data[i], color=color)

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
    
    print("\n" + "="*60)
    print("EXAMPLE 1: Simple Linear Plot")
    print("="*60)
    print(Lineplot([1, 2, 7], [9, -6, 8]).render())
    print(Lineplot(list(range(10))).render())
    
    # Generate x values for trig functions
    x_vals = [x/10 for x in range(-31, 62)]
    
    print("\n" + "="*60)
    print("EXAMPLE 2: Trigonometric Functions")
    print("="*60)
    print("SIN Function:")
    print(Lineplot(x_vals, math.sin).render())
    
    print("\nCOS Function:")
    print(Lineplot(x_vals, math.cos).render())
    
    print("\nSIN + COS Together:")
    print(Lineplot(x_vals, math.sin, x_vals, math.cos).render())
    
    print("\n" + "="*60)
    print("EXAMPLE 3: Logarithmic Scale Comparison")
    print("="*60)
    # Generate data with exponential growth
    x_log = list(range(1, 11))
    y_log = [2**n for n in x_log]
    
    print("With Linear Scale:")
    print(Lineplot(x_log, y_log).render())
    
    print("\nWith Logarithmic Scale (log2):")
    print(Lineplot(x_log, y_log, y_scale=lambda y: math.log2(y)).render())

    print("\n" + "="*60)
    print("EXAMPLE 4: Different Scaling Functions")
    print("="*60)
    
    # Generate sample data with wide range of values
    x_scale = list(range(1, 11))
    y_scale = [2**n for n in x_scale]  # Exponential growth [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
    
    print("Original Data (Linear Scale):")
    print(Lineplot(x_scale, y_scale).render())
    
    print("\nLogarithmic Scale (log2):")
    print(Lineplot(x_scale, y_scale, y_scale=lambda y: math.log2(y)).render())
    
    print("\nLogarithmic Scale (log10):")
    print(Lineplot(x_scale, y_scale, y_scale=lambda y: math.log10(y)).render())
    
    print("\nNatural Logarithm Scale (ln):")
    print(Lineplot(x_scale, y_scale, y_scale=lambda y: math.log(y)).render())
    
    print("\nSquare Root Scale:")
    print(Lineplot(x_scale, y_scale, y_scale=lambda y: math.sqrt(y)).render())
    
    print("\nCube Root Scale:")
    print(Lineplot(x_scale, y_scale, y_scale=lambda y: y**(1/3)).render())
    
    print("\nInverse Scale (1/y):")
    print(Lineplot(x_scale, y_scale, y_scale=lambda y: 1/y if y != 0 else 0).render())
    
    print("\nSymmetric Log Scale (for data with positive and negative values):")
    mixed_data = [-1000, -100, -10, -1, 0, 1, 10, 100, 1000]
    # A simple implementation of symlog that preserves sign
    symlog = lambda y: math.log10(abs(y)) * (1 if y >= 0 else -1) if y != 0 else 0
    print(Lineplot(range(len(mixed_data)), mixed_data, y_scale=symlog).render())
    
    print("\nMinMax Scale (normalize to 0-1 range):")
    y_min, y_max = min(y_scale), max(y_scale)
    print(Lineplot(x_scale, y_scale, y_scale=lambda y: (y - y_min) / (y_max - y_min)).render())
    
    print("\nZ-Score Standardization:")
    y_mean = sum(y_scale) / len(y_scale)
    y_std = math.sqrt(sum((y - y_mean)**2 for y in y_scale) / len(y_scale))
    print(Lineplot(x_scale, y_scale, y_scale=lambda y: (y - y_mean) / y_std).render())