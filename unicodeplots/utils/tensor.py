import os
import random

import numpy as np
import torch
from tinygrad import Tensor as TinyTensor

os.environ["CPU"] = "1"


def forward_op(name):
    def op(self, other):
        if isinstance(other, TensorAdapter):
            other = other.data
        result = getattr(self.data, name)(other)
        return TensorAdapter(result)

    return op


class TensorAdapter:
    def __init__(self, data):
        self.data = data

    def __getattr__(self, name):
        if name not in dir(self):
            return getattr(self.data, name)

    # to support python lists
    @staticmethod
    def _shape(x) -> tuple:
        if not isinstance(x, list):
            return ()
        if not x:
            return (0,)
        return (len(x), *TensorAdapter._shape(x[0]))

    @property
    def shape(self) -> tuple:
        if hasattr(self.data, "shape"):
            return self.data.shape
        if not isinstance(self.data, list):
            return ()
        if not self.data:
            return (0,)
        return self._shape(self.data)

    __add__ = forward_op("__add__")
    __radd__ = forward_op("__radd__")
    __sub__ = forward_op("__sub__")
    __rsub__ = forward_op("__rsub__")
    __mul__ = forward_op("__mul__")
    __rmul__ = forward_op("__rmul__")
    __truediv__ = forward_op("__truediv__")
    __rtruediv__ = forward_op("__rtruediv__")

    def __str__(self):
        if type(self.data).__module__ == "tinygrad.tensor":
            return f"tinygrad.tensor({self.data.tolist()})"
        return str(self.data)

    def __repr__(self):
        if type(self.data).__module__ == "tinygrad.tensor":
            return f"tinygrad.tensor({self.data.tolist()})"
        return repr(self.data)


if __name__ == "__main__":
    py = [[[random.random() * 255 for _ in range(3)] for _ in range(28)] for _ in range(28)]
    trch = torch.randint(0, 256, (28, 28, 3))
    nmpy = np.random.randint(0, 256, size=(28, 28, 3))
    tiny = TinyTensor.randint(28, 28, 3, low=0, high=256).tolist()
    pyt = TensorAdapter(py)
    trch = TensorAdapter(trch)
    nmpy = TensorAdapter(nmpy)
    tiny = TensorAdapter(tiny)
    print(pyt.shape, trch.shape, nmpy.shape, tiny.shape)
    a = TensorAdapter(TinyTensor([1]))
    b = TensorAdapter(TinyTensor(1))
    c = a + b
    print(c, a, b)
