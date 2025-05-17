import numpy as np
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
def test_imageplot_backends(snapshot, capsys, backend, snapshot_prefix):
    """Test Imageplot with various backends (numpy, pytorch, tinygrad, python lists)"""
    import random

    grayscale = rgb = None

    if backend == "numpy":
        grayscale = np.random.randint(0, 256, size=(28, 28), dtype=np.uint8)
        rgb = np.random.randint(0, 256, size=(28, 28, 3), dtype=np.uint8)
    elif backend == "pytorch":
        pytest.importorskip("torch")
        import torch

        grayscale = torch.randint(0, 256, (28, 28), dtype=torch.uint8)
        rgb = torch.randint(0, 256, (28, 28, 3), dtype=torch.uint8)
    elif backend == "tinygrad":
        pytest.importorskip("tinygrad")
        from tinygrad.tensor import Tensor

        grayscale = Tensor.rand(28, 28).mul(255)
        rgb = Tensor.rand(28, 28, 3).mul(255)
    elif backend == "python":
        grayscale = [[random.randint(0, 255) for _ in range(28)] for _ in range(28)]
        rgb = [[[random.randint(0, 255) for _ in range(3)] for _ in range(28)] for _ in range(28)]
    else:
        raise ValueError(f"Unknown backend: {backend}")

    # Render both images
    Imageplot(grayscale).render()
    captured_gray = capsys.readouterr()

    Imageplot(rgb).render()
    captured_rgb = capsys.readouterr()

    snapshot.assert_match(captured_gray.out, f"Imageplot_{snapshot_prefix}_Gray.txt")
    snapshot.assert_match(captured_rgb.out, f"Imageplot_{snapshot_prefix}_RGB.txt")
