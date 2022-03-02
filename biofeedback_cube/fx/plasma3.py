import numpy as np

from ..config import HEIGHT, WIDTH
from ..hydra import hydra
from ..palettes import palettes, cmap
from ..utils import sin, index_dict

yy, xx = np.mgrid[0:1:complex(0, HEIGHT), 0:1:complex(0, WIDTH)]


def plasma3(grid, t):
    palette = index_dict(palettes, hydra.a)

    tau = t * hydra.x
    f1 = .2 + hydra.y * 20
    f2 = .2 + hydra.b * 20
    f3 = .2 + hydra.c * 20
    f4 = .2 + hydra.f * 20
    f5 = .2 + hydra.g * 20

    field = sin(
        np.sin(2 * np.pi * f1 * yy + .25*tau)
        + np.sin(2 * np.pi * f2 * xx + .6*tau)
        + np.sin(10 * xx * f3 * yy + .41*tau)
        + np.sin(10 * xx**2 * f4 * yy**2 + .34*tau)
        + np.sin(10 * xx**2 * f5 * yy**2 + .34*tau)
    )

    r, g, b = cmap(palette, field)

    grid[:, :, 0] = r
    grid[:, :, 1] = g
    grid[:, :, 2] = b
