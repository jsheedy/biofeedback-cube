from biofeedback_cube.config import WIDTH, HEIGHT
from biofeedback_cube.hydra import hydra

import numpy as np

from ..utils import index_dict


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
    ], dtype=np.float64) / 255
}


def palette(grid, t):
    palette = index_dict(palettes, hydra.f)

    size = HEIGHT // len(palette)

    for i, color in enumerate(palette):
        grid[i*size:(i+1)*size, :, :] = color
