import colorsys
import random

import numpy as np

from biofeedback_cube.config import HEIGHT, WIDTH
from biofeedback_cube.hydra import hydra
from biofeedback_cube.utils import open_image, sin, cos


yy, xx = np.mgrid[0:1:complex(0, HEIGHT), 0:1:complex(0, WIDTH)]
iix = np.arange(WIDTH, dtype=np.int32)
iiy = np.arange(HEIGHT, dtype=np.int32)


def early_fire(grid, t):
    f = 10
    row = sin(f*t) > 0.5 and 1 or 0
    grid[row::4, :, 0] = 0.5
    grid[abs(1 - row)::4, :, 1] = 0.2
    grid[row::4, :, 2] = 0.0


def image(grid, t, fname, scale=1.0):

    x0 = int(-40 + 80 * (1-hydra.x))
    y0 = int(-40 + 80 * (1-hydra.y))

    rgba = open_image(fname, scale=scale)
    im = rgba[:, :, :3]
    im = im[::-1, ::-1, :]

    h, w = im.shape[:2]

    x_i = np.take(iix, range(x0, x0+w), mode='wrap')
    y_i = np.take(iiy, range(y0, y0+h), mode='wrap')

    xx_i, yy_i = np.meshgrid(x_i, y_i, sparse=True)

    grid[yy_i, xx_i, :] = im


def mario(grid, t):
    image(grid, t, 'mario.png', scale=0.28)


def tv_test(grid, t):
    image(grid, t, 'tv-test.png', scale=0.08)


def heart(grid, t):
    image(grid, t, 'heart.png', scale=0.12)


def jc(grid, t):
    image(grid, t, 'j+c.png', scale=0.3)


def circle(grid, t, color=(.7, .4, .2), weight=1.0):
    radius = hydra.f * 0.2

    if hydra.fresh(t):
        y = 1-hydra.y
        x = 1-hydra.x
    else:
        y = 0.25 + 0.5*sin(0.5*t)
        x = 0.25 + 0.5*cos(0.501*t)

    color = (hydra.a, hydra.b, hydra.c)
    mask = ((xx-x)**2 + (yy - y)**2) < radius
    grid[mask, :] += weight * np.array(color)


def tent(grid, t):
    """ similar to a circle but like a circus tent """
    r = 0.07 * hydra.f

    if hydra.fresh(t):
        y = 1-hydra.y
        x = 1-hydra.x
    else:
        y = 0.25 + 0.5*sin(0.5*t)
        x = 0.25 + 0.5*cos(0.501*t)

    tent = np.clip(1-np.sqrt((r*(xx-x))**2 + (r*(yy-y))**2), 0, 1)
    r, g, b = hydra.a, hydra.b, hydra.c

    grid[:, :, 0] = r * tent
    grid[:, :, 1] = g * tent
    grid[:, :, 2] = b * tent


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


def cmap(x):
    xp = [0.0, 0.66, 0.66, 0.78, 0.78, 0.82, 0.82, 1.0]

    rp = [0.0, 0.00, 1.00, 1.00, 0.5, 0.5, 0.2, 0.2]
    gp = [0.9, 0.90, 0.90, 0.90, 0.1, 0.1, 0.7, 0.7]
    bp = [1.0, 1.00, 0.75, 0.75, 0.3, 0.3, 0.4, 0.4]

    r = np.interp(x, xp, rp)
    g = np.interp(x, xp, gp)
    b = np.interp(x, xp, bp)

    return r, g, b


def clear(grid, rgb):
    grid[:] = rgb


def plasma2(grid, t):
    tau = t * hydra.f
    field = sin(
        np.sin(2 * np.pi * yy + .25*tau)
        + np.sin(2 * np.pi * xx + .6*tau)
        + np.sin(10 * xx * yy + .41*tau)
        + np.sin(10 * xx**2 * yy**2 + .34*tau)
    )

    r, g, b = cmap(field)
    grid[:, :, 0] = r
    grid[:, :, 1] = g
    grid[:, :, 2] = b


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
