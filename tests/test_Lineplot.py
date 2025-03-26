import math

from unicodeplots import Lineplot

# Test exp scaling
X_EXP = list(range(1, 11))
Y_EXP = [2**n for n in X_EXP]


# Testing Axis scaling
def test_lineplot_yscale():
    """
    Tests the README example of a simple line plot.
    """
    plot_linear = Lineplot(X_EXP, Y_EXP)
    plot_log2 = Lineplot(X_EXP, Y_EXP, yscale=lambda y: math.log2(y))

    assert plot_linear.min_x == 1
    assert plot_linear.max_x == 10
    assert plot_linear.min_y == 2
    assert plot_linear.max_y == 1024

    assert plot_log2.min_x == 1
    assert plot_log2.max_x == 10
    assert plot_log2.min_y == 1
    assert plot_log2.max_y == 10


print(Lineplot(X_EXP, Y_EXP, xscale=lambda x: x**2, yscale=lambda y: math.log2(y), border="ascii").render())
