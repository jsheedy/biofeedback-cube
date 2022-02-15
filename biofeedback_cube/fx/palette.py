from biofeedback_cube.config import WIDTH, HEIGHT
from biofeedback_cube.hydra import hydra

import numpy as np


palettes = {
    'rgb': [
        [255, 0, 0],
        [0, 255, 0],
        [0, 0, 255],
    ],
    'secondary': [
        [255, 255, 0],
        [255, 0, 255],
        [0, 255, 255],
    ],
    'geology': [
        [181, 210, 224],
        [184, 84, 94],
        [200, 141, 55],
        [168, 180, 76],
        [131, 87, 39],
        [56, 51, 51],
        [103, 128, 130]
    ]
}

def palette_map(x):
    """ return a palette for range d 0-1 the best range"""
    k = list(palettes.keys())
    return palettes[k[int(x * len(palettes))]]

def palette(grid, t):
    palette = palette_map(hydra.d)

    size = HEIGHT // len(palette)

    for i, color in enumerate(palette):
        r, g, b = color[0] / 255, color[1] / 255, color[2] / 255
        grid[i*size:(i+1)*size, :, :] = r, g, b
