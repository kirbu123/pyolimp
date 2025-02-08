from __future__ import annotations
import torch
from torch import Tensor
import segmentation_models_pytorch as smp

# import torchvision
from olimp.processing import fft_conv
from .download_path import download_path, PyOlimpHF


class PrecompensationUNETB0(smp.Unet):
    """
    .. image:: ../../../../_static/vdsr.svg
       :class: full-width
    """

    def __init__(
        self,
        encoder_name: str = "efficientnet-b0",
        encoder_wights: str = "imagenet",
        activation: str = "sigmoid",
        in_channels: int = 3,
        classes: int = 1,
    ) -> None:
        super().__init__(
            encoder_name=encoder_name,
            encoder_weights=encoder_wights,
            activation=activation,
            in_channels=in_channels,
            classes=classes,
        )

    @classmethod
    def from_path(cls, path: PyOlimpHF, **kwargs):
        model = cls(**kwargs)
        path = download_path(path)
        state_dict = torch.load(
            path, map_location=torch.get_default_device(), weights_only=True
        )
        model.load_state_dict(state_dict)
        return model

    def preprocess(self, image: Tensor, psf: Tensor) -> Tensor:
        # img_gray = image.to(torch.float32)[None, ...]
        # img_gray = torchvision.transforms.Resize((512, 512))(img_gray)
        img_blur = fft_conv(image, psf)

        return torch.cat(
            [
                image,
                img_blur,
                psf,
            ],
            dim=1,
        )

    def forward(self, image: Tensor) -> Tensor:
        return (super().forward(image),)

    def arguments(self, *args, **kwargs):
        return {}


def _demo():
    from ..._demo import demo
    from typing import Callable

    def demo_unet(
        image: torch.Tensor,
        psf: torch.Tensor,
        progress: Callable[[float], None],
    ) -> torch.Tensor:
        model = PrecompensationUNETB0.from_path(
            "hf://RVI/unet-efficientnet-b0.pth"
        )
        with torch.inference_mode():
            psf = psf.to(torch.float32)
            inputs = model.preprocess(image, psf)
            progress(0.1)
            (precompensation,) = model(inputs)
            progress(1.0)
            return precompensation

    demo("UNET", demo_unet, mono=True)


if __name__ == "__main__":
    _demo()
