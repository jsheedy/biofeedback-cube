from biofeedback_cube.config import WIDTH, HEIGHT
from biofeedback_cube.hydra import hydra

import numpy as np

from ..palettes import palettes
from ..utils import index_dict


def palette(grid, t):
    palette = index_dict(palettes, hydra.f)

    size = HEIGHT // len(palette.palette)

    for i, color in enumerate(palette.palette):
        grid[i*size:(i+1)*size, :, :] = color

