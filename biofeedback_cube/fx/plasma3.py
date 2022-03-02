import numpy as np

from ..config import HEIGHT, WIDTH
from ..hydra import hydra
from ..palettes import palettes, cmap
from ..utils import sin, index_dict

yy, xx = np.mgrid[0:1:complex(0, HEIGHT), 0:1:complex(0, WIDTH)]


def plasma3(grid, t):
    palette = index_dict(palettes, hydra.a)

    tau = 10 * t * hydra.b
    f1 = .1 + hydra.c * 5
    f2 = .1 + hydra.d * 5
    f3 = .1 + hydra.e * 5

    field = sin(
        hydra.x * np.sin(f1 * yy + .2 * tau)
        + hydra.y * np.sin(f2 * xx + .4 * tau)
        + hydra.f * np.sin(f3 * xx * yy + .6 * tau)
    )

    grid[:, :] = cmap(palette, field)
