import colorsys
import random

import numpy as np
from scipy.signal import sawtooth

from ..config import HEIGHT, WIDTH
from ..hydra import hydra
from ..palettes import palettes, cmap
from ..utils import sin, cos, index_dict, xx, yy


operators = (
    np.add,
    np.multiply,
    np.divide,
    np.power,
    np.subtract,
)


def early_fire(grid, t):
    f = 10
    row = sin(f*t) > 0.5 and 1 or 0
    grid[row::4, :, 0] = 0.5
    grid[abs(1 - row)::4, :, 1] = 0.2
    grid[row::4, :, 2] = 0.0


def cone(grid, t, operator=np.add):
    """ cone shape """
    palette = index_dict(palettes, hydra.a)

    r = 5 * hydra.f
    f = 10.0 * hydra.g

    if hydra.fresh(t):
        y = hydra.y
        x = hydra.x
    else:
        y = 0.5
        x = (sawtooth(f*t, width=0.5) + 1) / 2

    cone = np.clip(1-np.sqrt((r*(xx-x))**2 + (r*(yy-y))**2), 0, 1)
    mask = cone > 0
    grid[mask] = cmap(palette, cone)[mask]


def clear(grid, rgb):
    grid[:] = rgb


def plasma(grid, t):
    tau = t * hydra.f * 10
    f = .01 + hydra.g * 10
    field = (
        np.sin(2 * np.pi * f * yy + .25*tau)
        + np.sin(2 * np.pi * f * xx + .6*tau)
        + np.sin(10 * xx * f * yy + .41*tau)
        + np.sin(10 * xx**2 * f * yy**2 + .34*tau)
    )
    grid[:, :, 0] = hydra.a * sin(field)
    grid[:, :, 1] = hydra.b * sin(1.2*field + tau)
    grid[:, :, 2] = hydra.c * sin(0.2*field + 2*tau)


def plasma2(grid, t):
    tau = t * hydra.f
    field = sin(
        np.sin(2 * np.pi * yy + .25*tau)
        + np.sin(2 * np.pi * xx + .6*tau)
        + np.sin(10 * xx * yy + .41*tau)
        + np.sin(10 * xx**2 * yy**2 + .34*tau)
    )

    grid[:, :] = cmap(palettes['plasma2'], field)


def strobe(grid, t):
    f = .1 + 100 * hydra.f
    r, g, b = (hydra.a, hydra.b, hydra.c)
    if hydra.f >= 0.99 or sin(f*t) > .5:
        clear(grid, (r, g, b))
    else:
        clear(grid, (0, 0, 0))


def starfield(grid, t):
    for i in range(int(30*hydra.x)):
        y = random.randint(0, HEIGHT-1)
        x = random.randint(0, WIDTH-1)
        grid[y, x, :] = random.random(), random.random(), random.random()


def test_grid(grid, t, WIDTH=3, weight=1.0):
    if hydra.fresh(t):
        y = int((HEIGHT-1) * hydra.a)
    else:
        f = (hydra.b / .5) ** 2
        y = int(sin(f*t)*(HEIGHT-1))

    h = sin(.2*t)
    s = .5 + .5*cos(.1*t)
    v = .5 + 0.5*cos(t)*sin(t)
    color = colorsys.hsv_to_rgb(h, s, v)
    grid[y, :, :] += color
