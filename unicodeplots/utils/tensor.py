import os
import random
from collections.abc import Iterable

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

    @staticmethod
    def _coerce_to_int(value):
        if isinstance(value, TensorAdapter):
            return TensorAdapter._coerce_to_int(value.data)
        if isinstance(value, list):
            return [TensorAdapter._coerce_to_int(item) for item in value]
        if isinstance(value, (int, float)):
            return int(value)
        if hasattr(value, "int"):
            return value.int()
        if hasattr(value, "astype"):
            return value.astype("int")
        return value  # fall back unchanged

    def to_int(self):
        self.data = self._coerce_to_int(self.data)
        return self

    # to support python lists
    @staticmethod
    def _resolve_shape(value):
        if isinstance(value, TensorAdapter):
            return TensorAdapter._resolve_shape(value.data)
        if hasattr(value, "shape"):
            return tuple(value.shape)
        if not isinstance(value, list):
            return ()
        if not value:
            return (0,)
        return (len(value), *TensorAdapter._resolve_shape(value[0]))

    @property
    def shape(self) -> tuple:
        return self._resolve_shape(self.data)

    def __getitem__(self, key) -> "TensorAdapter":
        if isinstance(key, tuple):
            idx = self.data
            for v in key:
                idx = idx[v]
            return TensorAdapter(idx)
        return TensorAdapter(self.data[key])

    def __iter__(self):
        if isinstance(self.data, Iterable):
            for item in self.data:
                yield TensorAdapter(item)
        else:
            raise TypeError("Cannot iterate over non-list data")

    def __int__(self) -> int:
        return int(self.data)

    ## Math ops
    __add__ = forward_op("__add__")
    __radd__ = forward_op("__radd__")
    __sub__ = forward_op("__sub__")
    __rsub__ = forward_op("__rsub__")
    __mul__ = forward_op("__mul__")
    __rmul__ = forward_op("__rmul__")
    __truediv__ = forward_op("__truediv__")
    __rtruediv__ = forward_op("__rtruediv__")
    __matmul__ = forward_op("__matmul__")
    __imatmul__ = forward_op("__imatmul__")
    __len__ = forward_op("__len__")

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
    tiny = TinyTensor.randint(28, 28, 3, low=0, high=256)
    pyt = TensorAdapter(py)
    trch = TensorAdapter(trch)
    nmpy = TensorAdapter(nmpy)
    tiny = TensorAdapter(tiny)
    print(pyt.shape, trch.shape, nmpy.shape, tiny.shape)
    a = TensorAdapter(TinyTensor([1]))
    b = TensorAdapter(TinyTensor(1))
    c = a + b
    print(c, a, b)
