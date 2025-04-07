from unicodeplots.plots.lineplot import Lineplot

__all__ = ["Lineplot"]

try:
    from unicodeplots.plots.imageplot import Imageplot  # noqa: F401

    __all__.extend(["Imageplot"])
except ImportError:
    print("Pillow is not installed. Imageplot will not be available.")
    pass
