from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt
from importlib import import_module


def save_demo(root: Path, module: str, name: str) -> None:
    path = root / f"{name}.svg"
    if path.exists():
        print(f"skipping {path}")
        return
    module = import_module(module)
    print(f"saving {path}")
    plt.show = lambda: plt.savefig(path)
    module._demo()


def main() -> None:
    root = Path(__file__).parent / "source" / "_static"
    root.mkdir(exist_ok=True, parents=True)

    for module, name in (
        ("olimp.precompensation.optimization.montalto", "montalto"),
        ("olimp.precompensation.optimization.bregman_jumbo", "bregman_jumbo"),
        (
            "olimp.precompensation.optimization.tennenholtz_zachevsky",
            "tennenholtz_zachevsky",
        ),
        ("olimp.precompensation.basic.huang", "huang"),
        ("olimp.precompensation.analytics.feng_xu", "feng_xu"),
        ("olimp.precompensation.nn.models.vae", "vae"),
        ("olimp.precompensation.nn.models.cvae", "cvae"),
        ("olimp.precompensation.nn.models.vdsr", "vdsr"),
        (
            "olimp.precompensation.nn.models.unet_efficient_b0",
            "unet_efficient_b0",
        ),
        ("olimp.precompensation.nn.models.dwdn.__main__", "dwdn"),
        # ("olimp.precompensation.nn.models.cvd_swin", "cvd_swin"), not implemented yet
    ):
        save_demo(root, module, name)


if __name__ == "__main__":
    main()
