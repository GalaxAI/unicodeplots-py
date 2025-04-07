import math
import os
from random import seed, uniform

import pytest

from unicodeplots.plots import Imageplot, Lineplot
from unicodeplots.plots.imageplot import SUPPORTED_TERM

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

    plot = Lineplot(x, y, scatter=True, border="single", title="Random Scatter Plot", show_axes=True)
    output = plot.render()
    snapshot.assert_match(output, "Lineplot_Example_03.txt")


def test_lineplot_example_04(snapshot):
    seed(42)
    x = [uniform(-5, 5) for _ in range(100)]
    y = [uniform(-5, 5) for _ in range(100)]
    x1 = [uniform(-5, 5) for _ in range(100)]
    y1 = [uniform(-5, 5) for _ in range(100)]

    plot = Lineplot(x, y, x1, y1, width=40, height=20, scatter=True, border="single", marker=["*", "x"], title="Scatter Plot w Marker", show_axes=True)
    output = plot.render()
    snapshot.assert_match(output, "Lineplot_Example_04.txt")


def test_imageplot_example_01(snapshot, capsys):
    if os.environ.get("CI"):
        pytest.skip("Skipping Kitty protocol test in CI environment")

    term = os.environ.get("TERM", "")
    if term.lower() not in SUPPORTED_TERM:
        pytest.skip("Terminal doesn't support Kitty protocol")

    # With kitty protocol
    Imageplot("media/monarch.png").render()
    captured = capsys.readouterr()
    snapshot.assert_match(captured.out, "Imageplot_Example_01.txt")


def test_imageplot_example_02(snapshot, capsys, monkeypatch):
    # Without kitty protocol
    monkeypatch.setenv("ASCII", "1")
    Imageplot("media/monarch.png").render()
    captured = capsys.readouterr()
    snapshot.assert_match(captured.out, "Imageplot_Example_02.txt")
