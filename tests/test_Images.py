import pytest

from unicodeplots.plots import Imageplot


@pytest.mark.parametrize(
    "backend,snapshot_prefix",
    [
        ("numpy", "Numpy"),
        ("pytorch", "PyTorch"),
        ("tinygrad", "TinyGrad"),
        ("python", "Python"),
    ],
)
@pytest.mark.parametrize(
    "dtype",
    [
        "int",
        "float",
        "int8",
        "uint8",
        "float32",
        "float64",
    ],
)
def test_imageplot_backends(backend, snapshot_prefix, dtype):
    """Test Imageplot with various backends and dtypes (numpy, pytorch, tinygrad, python lists)"""
    import random

    grayscale = rgb = None

    if backend == "numpy":
        pytest.importorskip("numpy")
        import numpy as np

        np_dtype = {
            "int": int,
            "float": float,
            "int8": np.int8,
            "uint8": np.uint8,
            "float32": np.float32,
            "float64": np.float64,
        }[dtype]
        grayscale = np.random.randint(0, 256, size=(28, 28)).astype(np_dtype)
        rgb = np.random.randint(0, 256, size=(28, 28, 3)).astype(np_dtype)
        grayscale = grayscale.tolist()
        rgb = rgb.tolist()
    elif backend == "pytorch":
        pytest.importorskip("torch")
        import torch

        torch_dtype = {
            "int": torch.int32,
            "float": torch.float32,
            "int8": torch.int8,
            "uint8": torch.uint8,
            "float32": torch.float32,
            "float64": torch.float64,
        }[dtype]
        if dtype == "int8":
            low, high = -128, 128
        elif dtype == "uint8":
            low, high = 0, 256
        else:
            low, high = 0, 256
        if "int" in dtype or "uint" in dtype:
            grayscale = torch.randint(low, high, (28, 28), dtype=torch_dtype)
            rgb = torch.randint(low, high, (28, 28, 3), dtype=torch_dtype)
        else:
            grayscale = torch.rand(28, 28, dtype=torch_dtype) * 255
            rgb = torch.rand(28, 28, 3, dtype=torch_dtype) * 255
        grayscale = grayscale.tolist()
        rgb = rgb.tolist()
    elif backend == "tinygrad":
        pytest.importorskip("tinygrad")
        from tinygrad.dtype import dtypes as tg_dtypes
        from tinygrad.tensor import Tensor

        tg_dtype = {
            "int": tg_dtypes.int32,
            "float": tg_dtypes.float32,
            "int8": tg_dtypes.int8,
            "uint8": tg_dtypes.uint8,
            "float32": tg_dtypes.float32,
            "float64": tg_dtypes.float64,
        }[dtype]

        if "int" in dtype or "uint" in dtype:
            grayscale = Tensor.randint(28, 28, low=0, high=256, dtype=tg_dtype).tolist()
            rgb = Tensor.randint(28, 28, 3, low=0, high=256, dtype=tg_dtype).tolist()
        else:
            grayscale = Tensor.rand(28, 28, dtype=tg_dtype).mul(255).tolist()
            rgb = Tensor.rand(28, 28, 3, dtype=tg_dtype).mul(255).tolist()
    elif backend == "python":
        py_dtype = {
            "int": int,
            "float": float,
            "int8": int,
            "uint8": int,
            "float32": float,
            "float64": float,
        }[dtype]

        grayscale = [[py_dtype(random.random() * 255) for _ in range(28)] for _ in range(28)]
        rgb = [[[py_dtype(random.random() * 255) for _ in range(3)] for _ in range(28)] for _ in range(28)]

    else:
        raise ValueError(f"Unknown backend: {backend}")

    # Render both images (should not raise)
    Imageplot(grayscale).render()
    Imageplot(rgb).render()
