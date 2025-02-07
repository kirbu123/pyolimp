from __future__ import annotations
import torch
import torch.nn.functional as F


def resize_kernel(
    kernel: torch.Tensor, target_size: tuple[int, int]
) -> torch.Tensor:
    """
    Rescales kernel to `target_size`
    """
    resized_kernel = F.interpolate(
        kernel, size=target_size, mode="bilinear", align_corners=True
    )

    return resized_kernel


def fft_conv(image: torch.Tensor, kernel: torch.Tensor) -> torch.Tensor:
    """
    FFT base method for fast convolution. Input types are expected to be
    `float32` and size must be equal
    """
    assert image.dtype == torch.float32, image.dtype
    assert kernel.dtype == torch.float32, kernel.dtype
    assert (
        image.shape[-2:] == kernel.shape[-2:]
    ), f"Expected equal shapes, got: image={image.shape[-2:]}, kernel={kernel.shape[-2:]}"

    return torch.real(
        torch.fft.ifft2(torch.fft.fft2(image) * torch.fft.fft2(kernel))
    )


def scale_value(
    arr: torch.Tensor,
    min_val: float = 0.0,
    max_val: float = 1.0,
) -> torch.Tensor:
    """
    Rescale values making minimum equal `min_val` and maximum equal `max_val`
    """
    black, white = arr.min(), arr.max()
    if black == white:
        mul = 0.0
        if min_val <= black <= max_val:
            add = black
        else:
            add = (
                min_val
                if abs(black - min_val) <= abs(black - max_val)
                else max_val
            )
    else:
        mul = (max_val - min_val) / (white - black)
        add = -black * mul + min_val
    out = torch.mul(arr, mul)
    out += add
    return out
