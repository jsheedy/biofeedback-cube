from functools import partial

import numpy as np

class Palette:
    def __init__(self, palette: np.array):
        self.palette = palette
        xp = np.linspace(0, 255, len(palette), dtype=np.uint8)

        rp = palette[:, 0]
        gp = palette[:, 1]
        bp = palette[:, 2]

        r = [np.interp(x, xp, rp) for x in range(256)]
        g = [np.interp(x, xp, gp) for x in range(256)]
        b = [np.interp(x, xp, bp) for x in range(256)]

        self.lut = np.array([r, g, b], dtype=np.float64).T

    def __len__(self):
        return len(self.lut)


palettes = {
    'rgb': Palette(np.array([
        [255, 0, 0],
        [0, 255, 0],
        [0, 0, 255],
    ], dtype=np.float64) / 255),

    'secondary': Palette(np.array([
        [255, 255, 0],
        [255, 0, 255],
        [0, 255, 255],
    ], dtype=np.float64) / 255),

    'geology': Palette(np.array([
        [181, 210, 224],
        [184, 84, 94],
        [200, 141, 55],
        [168, 180, 76],
        [131, 87, 39],
        [56, 51, 51],
        [103, 128, 130]
    ], dtype=np.float64) / 255),

    'jbl': Palette(np.array([
        [149, 175, 240],
        [224, 150, 35],
        [107, 95, 157],
        [168, 178, 107],
        [80, 94, 42],
    ], dtype=np.float64) / 255),

    # see https://cran.r-project.org/web/packages/viridis/vignettes/intro-to-viridis.html
    'plasma': Palette(np.array([
        [242, 248, 67],
        [221, 141, 75],
        [176, 72, 120],
        [160, 60, 150],
        [91, 39, 163],
        [23, 28, 132],
    ], dtype=np.float64) / 255),

    'viridis': Palette(np.array([
        [246, 230, 66],
        [141, 204, 98],
        [86, 144, 139],
        [67, 73, 133],
        [61, 21, 83],
    ], dtype=np.float64) / 255),
}


def cmap(palette: Palette, field: np.array):
    idx = (field * 255).astype(np.uint8)
    return palette.lut[idx]
