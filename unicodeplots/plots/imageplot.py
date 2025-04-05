from typing import Optional


class Imageplot:
    """
    A class for creating plots with Unicode chars of images.
    """

    def __init__(
        self,
        *args,  # *Images
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        border: Optional[str] = "",
        legend: bool = False,
        **kwrags,
    ):
        """
        ...
        """
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.legend = legend
        self.border_style = border

        self.canvas = None  # ImageCanvas(**kwargs)
        self.plot()

    def plot(self):
        pass

    def render(self):
        pass
