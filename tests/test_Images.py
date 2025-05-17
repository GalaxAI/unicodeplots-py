import numpy as np
import pytest

from unicodeplots.plots import Imageplot


def test_imageplot_numpy(snapshot, capsys):
    """Test Imageplot with numpy arrays (grayscale and RGB)"""
    # Create a 28x28 grayscale image (values between 0 and 255)
    grayscale = np.random.randint(0, 256, size=(28, 28), dtype=np.uint8)

    # Create a 28x28 RGB image
    rgb = np.random.randint(0, 256, size=(28, 28, 3), dtype=np.uint8)

    # Render both images
    Imageplot(grayscale).render()
    captured_gray = capsys.readouterr()

    Imageplot(rgb).render()
    captured_rgb = capsys.readouterr()

    snapshot.assert_match(captured_gray.out, "Imageplot_Numpy_Gray.txt")
    snapshot.assert_match(captured_rgb.out, "Imageplot_Numpy_RGB.txt")


def test_imageplot_pytorch(snapshot, capsys):
    """Test Imageplot with PyTorch tensors (grayscale and RGB)"""
    pytest.importorskip("torch")
    import torch

    # Create a 28x28 grayscale image
    grayscale = torch.randint(0, 256, (28, 28), dtype=torch.uint8)

    # Create a 28x28 RGB image
    rgb = torch.randint(0, 256, (28, 28, 3), dtype=torch.uint8)

    # Render both images
    Imageplot(grayscale).render()
    captured_gray = capsys.readouterr()

    Imageplot(rgb).render()
    captured_rgb = capsys.readouterr()

    snapshot.assert_match(captured_gray.out, "Imageplot_PyTorch_Gray.txt")
    snapshot.assert_match(captured_rgb.out, "Imageplot_PyTorch_RGB.txt")


def test_imageplot_tinygrad(snapshot, capsys):
    """Test Imageplot with TinyGrad tensors (grayscale and RGB)"""
    pytest.importorskip("tinygrad")
    from tinygrad.tensor import Tensor

    # Create a 28x28 grayscale image
    grayscale = Tensor.rand(28, 28).mul(255)

    # Create a 28x28 RGB image
    rgb = Tensor.rand(28, 28, 3).mul(255)

    # Render both images
    Imageplot(grayscale).render()
    captured_gray = capsys.readouterr()

    Imageplot(rgb).render()
    captured_rgb = capsys.readouterr()

    snapshot.assert_match(captured_gray.out, "Imageplot_TinyGrad_Gray.txt")
    snapshot.assert_match(captured_rgb.out, "Imageplot_TinyGrad_RGB.txt")


def test_imageplot_python(snapshot, capsys):
    """Test Imageplot with pure Python lists (grayscale and RGB)"""
    import random

    # Create a 28x28 grayscale image with nested lists
    grayscale = [[random.randint(0, 255) for _ in range(28)] for _ in range(28)]

    # Create a 28x28 RGB image with nested lists
    rgb = [[[random.randint(0, 255) for _ in range(3)] for _ in range(28)] for _ in range(28)]

    # Render both images
    Imageplot(grayscale).render()
    captured_gray = capsys.readouterr()

    Imageplot(rgb).render()
    captured_rgb = capsys.readouterr()

    snapshot.assert_match(captured_gray.out, "Imageplot_Python_Gray.txt")
    snapshot.assert_match(captured_rgb.out, "Imageplot_Python_RGB.txt")
