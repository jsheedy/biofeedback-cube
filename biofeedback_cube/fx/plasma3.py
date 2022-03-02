import numpy as np

from ..config import HEIGHT, WIDTH
from ..hydra import hydra
from ..palettes import palettes, cmap
from ..utils import sin, index_dict

yy, xx = np.mgrid[0:1:complex(0, HEIGHT), 0:1:complex(0, WIDTH)]


def plasma3(grid, t):
    palette = index_dict(palettes, hydra.a)

    tau = t * hydra.a
    f2 = .2 + hydra.b * 5
    f3 = .2 + hydra.c * 5
    f1 = .2 + hydra.d * 5

    field = sin(
        hydra.x * np.sin(2 * np.pi * f1 * yy + .25 * tau)
        + hydra.y * np.sin(2 * np.pi * f2 * xx + .6 * tau)
        + hydra.e * np.sin(10 * xx * f3 * yy + .41 * tau)
    )

    grid[:, :] = cmap(palette, field)
