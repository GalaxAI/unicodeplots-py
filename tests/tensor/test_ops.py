import unittest
from typing import Callable

import numpy as np
import torch
from tinygrad import Tensor as TinyTensor

from unicodeplots.utils.tensor import TensorAdapter


def helper_test_op(shps, fxn: Callable, low=-1, high=1, skip_py=False):
    tst = prepare_test_op(low, high, shps, skip_py)
    for ts in tst:
        _ = fxn(*ts)


def prepare_test_op(low, high, shps, skip_py=False):
    np.random.seed(0)
    py_data = [np.random.uniform(low=low, high=high, size=size).tolist() for size in shps]
    np_data = [np.array(data) for data in py_data]
    t_data = [torch.tensor(data, requires_grad=False) for data in np_data]
    tiny_data = [TinyTensor(data) for data in np_data]
    all_data = [py_data, np_data, t_data, tiny_data]
    tst = []
    if skip_py:
        all_data = all_data[1:]
    for data in all_data:
        tst.append([TensorAdapter(d) for d in data])
    return tst


class TestOps(unittest.TestCase):
    ## Add
    def test_add(self):
        helper_test_op([(45, 68), (45, 68)], lambda x, y: x + y)
        helper_test_op([(3, 3, 3), (3, 3, 3)], lambda x, y: x + y)
        helper_test_op([(), ()], lambda x, y: x + y)

    def test_add3(self):
        helper_test_op([(45, 65), (45, 65), (45, 65)], lambda x, y, z: x + y + z)

    def test_broadcasted_add(self):
        helper_test_op([(45, 65), (45, 1)], lambda x, y: x + y)
        helper_test_op([(45, 65), ()], lambda x, y: x + y, skip_py=True)

    def test_broadcasted_add_2(self):
        helper_test_op([(45, 65), (65,)], lambda x, y: x + y)


if __name__ == "__main__":
    unittest.main()
    # TestOps()
