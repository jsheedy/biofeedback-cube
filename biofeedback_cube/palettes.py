from functools import partial

import numpy as np


palettes = {
    'rgb': np.array([
        [255, 0, 0],
        [0, 255, 0],
        [0, 0, 255],
    ], dtype=np.float64) / 255,

    'secondary': np.array([
        [255, 255, 0],
        [255, 0, 255],
        [0, 255, 255],
    ], dtype=np.float64) / 255,

    'geology': np.array([
        [181, 210, 224],
        [184, 84, 94],
        [200, 141, 55],
        [168, 180, 76],
        [131, 87, 39],
        [56, 51, 51],
        [103, 128, 130]
    ], dtype=np.float64) / 255,

    'jbl': np.array([
        [149, 175, 240],
        [224, 150, 35],
        [107, 95, 157],
        [168, 178, 107],
        [80, 94, 42],
    ], dtype=np.float64) / 255,

    # see https://cran.r-project.org/web/packages/viridis/vignettes/intro-to-viridis.html
    'plasma': np.array([
        [242, 248, 67],
        [221, 141, 75],
        [176, 72, 120],
        [91, 39, 163],
        [23, 28, 132],
    ], dtype=np.float64) / 255,

    'viridis': np.array([
        [246, 230, 66],
        [141, 204, 98],
        [86, 144, 139],
        [67, 73, 133],
        [61, 21, 83],
    ], dtype=np.float64) / 255,
}


def f(x: float, palette=None):
    xp = np.linspace(0, 1, len(palette))

    rp = palette[:, 0]
    gp = palette[:, 1]
    bp = palette[:, 2]

    r = np.interp(x, xp, rp)
    g = np.interp(x, xp, gp)
    b = np.interp(x, xp, bp)

    return r, g, b


def cmap(palette: np.array, field: np.array):
    g = partial(f, palette=palette)
    r, g, b = np.vectorize(g)(field)
    return r, g, b
