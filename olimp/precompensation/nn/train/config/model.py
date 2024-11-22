from __future__ import annotations
from typing import Annotated, Literal
from pydantic import Field
from .base import StrictModel


class ModelConfig(StrictModel):
    pass


class VDSR(ModelConfig):
    name: Literal["vdsr"]
    path: str | None = None

    def get_instance(self):
        from ...models.vdsr import VDSR

        if self.path is not None:
            return VDSR.from_path(path=self.path)
        return VDSR()


class VAE(ModelConfig):
    name: Literal["vae"]
    path: str | None = None

    def get_instance(self):
        from ...models.vae import VAE

        if self.path is not None:
            return VAE.from_path(path=self.path)
        return VAE()


class CVAE(ModelConfig):
    name: Literal["cvae"]
    path: str | None = None

    def get_instance(self):
        from ...models.cvae import CVAE

        if self.path is not None:
            return CVAE.from_path(path=self.path)
        return CVAE()


class UNET_b0(ModelConfig):
    name: Literal["unet_b0"]
    path: str | None = None

    def get_instance(self):
        from ...models.unet_efficient_b0 import PrecompensationUNETB0

        if self.path is not None:
            return PrecompensationUNETB0.from_path(path=self.path)
        return PrecompensationUNETB0()


class PrecompensationUSRNet(ModelConfig):
    name: Literal["precompensationusrnet"]
    path: str | None = None

    n_iter: int = 8
    h_nc: int = 64
    in_nc: int = 4
    out_nc: int = 3
    nc: list[int] = [64, 128, 256, 512]
    nb: int = 2

    def get_instance(self):
        from ...models.usrnet import PrecompensationUSRNet

        if self.path is not None:
            return PrecompensationUSRNet.from_path(path=self.path)
        return PrecompensationUSRNet(
            n_iter=self.n_iter,
            h_nc=self.h_nc,
            in_nc=self.in_nc,
            out_nc=self.out_nc,
            nc=self.nc,
            nb=self.nb,
        )


class PrecompensationDWDN(ModelConfig):
    name: Literal["precompensationdwdn"]
    n_levels: int = 1
    path: str | None = None

    def get_instance(self):
        from ...models.dwdn import PrecompensationDWDN

        if self.path is not None:
            return PrecompensationDWDN.from_path(path=self.path)
        return PrecompensationDWDN(n_levels=self.n_levels)


class Generator_transformer_pathch4_844_48_3_nouplayer_server5(ModelConfig):
    name: Literal["Generator_transformer_pathch4_844_48_3_nouplayer_server5"]
    path: str | None = None

    def get_instance(self):
        from ...models.cvd_swin.Generator_transformer_pathch4_844_48_3_nouplayer_server5 import (
            Generator_transformer_pathch4_844_48_3_nouplayer_server5,
        )

        if self.path is not None:
            return Generator_transformer_pathch4_844_48_3_nouplayer_server5.from_path(
                path=self.path
            )

        return Generator_transformer_pathch4_844_48_3_nouplayer_server5()


Model = Annotated[
    VDSR
    | VAE
    | CVAE
    | UNET_b0
    | PrecompensationUSRNet
    | PrecompensationDWDN
    | Generator_transformer_pathch4_844_48_3_nouplayer_server5,
    Field(..., discriminator="name"),
]
