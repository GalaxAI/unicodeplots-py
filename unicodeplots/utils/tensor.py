import os
import random
from collections.abc import Iterable

import numpy as np
import torch
from tinygrad import Tensor as TinyTensor

os.environ["CPU"] = "1"


class Tensor:
    def __init__(self, data):
        if isinstance(data, Iterable):
            try:
                self.data = [Tensor(x) for x in data]
            except TypeError:  # pytorch d0 is iterable
                self.data = data.item()
        else:
            self.data = data

    def shape(self) -> tuple:
        if hasattr(self.data, "shape"):
            return self.data.shape
        if not isinstance(self.data, list):
            return ()
        if not self.data:
            return (0,)
        return (len(self.data), *self.data[0].shape())

    def __add__(self, other) -> "Tensor":
        return Tensor(self.data + other.data)

    def __sub__(self, other) -> "Tensor":
        return Tensor(self.data - other.data)

    def __mul__(self, other) -> "Tensor":
        return Tensor(self.data * other.data)

    def __truediv__(self, other) -> "Tensor":
        return Tensor(self.data / other.data)

    def __str__(self):
        if type(self.data).__module__ == "tinygrad.tensor":
            return f"Tensor({self.data.tolist()})"
        return f"Tensor({self.data})"

    def __repr__(self):
        if type(self.data).__module__ == "tinygrad.tensor":
            return f"Tensor({self.data.tolist()})"
        return f"Tensor({self.data})"


if __name__ == "__main__":
    py = [[[random.random() * 255 for _ in range(3)] for _ in range(28)] for _ in range(28)]
    trch = torch.randint(0, 256, (28, 28, 3))
    nmpy = np.random.randint(0, 256, size=(28, 28, 3))
    tiny = TinyTensor.randint(28, 28, 3, low=0, high=256).tolist()
    for _ in range(1):
        pyt = Tensor(py)
        trch = Tensor(trch)
        nmpy = Tensor(nmpy)
        tiny = Tensor(tiny)
        print(pyt.shape(), trch.shape(), nmpy.shape(), tiny.shape())
    # a = [1, 1, 1]
    # b = [2, 2, 2]
    # print("HELLO")
    # for t in [torchTensor, np_array, TinyTensor]:
    #     a_t = t(a)
    #     b_t = t(b)
    #     c_t = a_t / b_t
    #     print(a_t, b_t, c_t)
    #     c = Tensor(a_t) / Tensor(b_t)
    #     print(c, c.data == c_t)
    # print("HELLO")
#
