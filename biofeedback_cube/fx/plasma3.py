import numpy as np

from ..config import HEIGHT, WIDTH
from ..hydra import hydra
from ..palettes import palettes, cmap
from ..utils import sin, index_dict, xx, yy


def plasma3(grid, t):
    palette = index_dict(palettes, hydra.a)

    tau = 10 * t * hydra.b
    f1 = hydra.c * 10
    f2 = hydra.f * 8
    f3 = hydra.g * 6

    field = sin(
        hydra.x * np.sin(f1 * yy + .2 * tau)
        + hydra.y * np.sin(f2 * xx + .4 * tau)
        + hydra.f * np.sin(f3 * xx * yy + 2 * np.pi * sin(0.2 * tau))
    )

    grid[:, :] = cmap(palette, field)
