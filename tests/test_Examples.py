import math
from random import seed, uniform

from unicodeplots import Lineplot

# The first time you run this, pytest-snapshot will save 'output'
# Subsequent runs will compare 'output' to the saved version.


def test_lineplot_example_01(snapshot):
    """
    Tests the README example of a simple line plot.
    """
    x = [-1, 2, 3, 7]
    y = [-1, 2, 9, 4]
    plot = Lineplot(x, y, title="Simple Plot", xlabel="x", ylabel="x", border="single")
    output = plot.render()

    snapshot.assert_match(output, "Lineplot_Example_01.txt")


def test_lineplot_example_02(snapshot):
    x_vals = [x / 10 for x in range(-31, 62)]
    plot = Lineplot(x_vals, math.sin, x_vals, math.cos, width=80, height=60, show_axes=True, border="single", xlabel="x", ylabel="f(x)")
    output = plot.render()
    snapshot.assert_match(output, "Lineplot_Example_02.txt")


def test_lineplot_example_03(snapshot):
    seed(42)
    x = [uniform(-5, 5) for _ in range(100)]
    y = [uniform(-5, 5) for _ in range(100)]

    plot = Lineplot(x, y, scatter=True, title="Random Scatter Plot", show_axes=True)
    output = plot.render()
    snapshot.assert_match(output, "Lineplot_Example_03.txt")
