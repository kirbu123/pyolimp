from __future__ import annotations
from typing import Annotated, Literal, Any, TypeAlias
from .base import StrictModel
from pydantic import Field, confloat
from olimp.processing import conv
from .....simulate import Distortion
from torch import Tensor
import torch


class VaeLossFunction(StrictModel):
    name: Literal["Vae"]

    def load(self, model: Any):
        from ...models.vae import VAE
        from .....evaluation.loss import vae_loss

        assert isinstance(
            model, VAE
        ), f"Vae loss only work with Vae model, not {model}"

        def f(model_output: list[Tensor], datums: list[Tensor]) -> Tensor:
            image, psf = datums
            precompensated, *args = model_output
            retinal_precompensated = conv(
                precompensated.to(torch.float32).clip(0, 1), psf
            )
            loss = vae_loss(retinal_precompensated, image, *args)
            return loss

        return f


Degree: TypeAlias = Literal[10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
CBType: TypeAlias = Literal["protan", "deutan"]


class ColorBlindnessLossFunction(StrictModel):
    name: Literal["ColorBlindnessLoss"]
    type: CBType
    degree: Degree = 100
    lambda_ssim: Annotated[float, confloat(ge=0, le=1)] = 0.25
    global_points: int = 3000

    def load(self, _model: Any):
        from .....evaluation.loss.color_blindness_loss import (
            ColorBlindnessLoss,
        )

        cbl = ColorBlindnessLoss(
            cb_type=self.type,
            degree=self.degree,
            lambda_ssim=self.lambda_ssim,
            global_points=self.global_points,
        )

        def f(model_output: list[Tensor], datums: list[Tensor]) -> Tensor:
            (image,) = datums
            assert image.ndim == 4, image.ndim
            (precompensated,) = model_output
            assert precompensated.ndim == 4, precompensated.ndim
            return cbl(image, precompensated)

        return f


class MultiScaleSSIMLossFunction(StrictModel):
    name: Literal["MS_SSIM"]

    kernel_size: int = 11
    kernel_sigma: float = 1.5
    k1: float = 0.01
    k2: float = 0.03

    def load(self, _model: Any):
        from piq import MultiScaleSSIMLoss

        ms_ssim = MultiScaleSSIMLoss(
            kernel_size=self.kernel_size,
            kernel_sigma=self.kernel_sigma,
            k1=self.k1,
            k2=self.k2,
        )

        def f(
            model_output: list[Tensor],
            datums: list[Tensor],
            distortions: list[type[Distortion]],
        ) -> Tensor:
            assert isinstance(model_output, tuple | list)
            assert isinstance(datums, tuple | list)
            distorted: list[Tensor] = []
            for distortion, d_input in zip(
                distortions, datums[1:], strict=True
            ):
                distorted.append(
                    distortion(d_input)(*model_output).clip(min=0.0, max=1.0)
                )
            original_image = datums[0]
            return ms_ssim(*distorted, original_image)

        return f


LossFunction = Annotated[
    VaeLossFunction | ColorBlindnessLossFunction | MultiScaleSSIMLossFunction,
    Field(..., discriminator="name"),
]
