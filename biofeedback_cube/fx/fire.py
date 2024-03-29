"""
https://lodev.org/cgtutor/fire.html
"""

from biofeedback_cube.config import WIDTH, HEIGHT
from biofeedback_cube.hydra import hydra

import numpy as np
from scipy.signal import convolve2d

fire_grid = np.zeros(shape=(HEIGHT + 1, WIDTH), dtype=np.float32)

kernel = np.array([
    [0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0],
    [1.0, 1.0, 1.0],
    [0.0, 1.0, 0.0],
], dtype=np.float32)


def fire(grid, t):
    global fire_grid
    fire_grid[0, :] = np.random.random((1, WIDTH))
    modulated_kernel = kernel / (3.5 + 2 * hydra.f)
    fire_grid = convolve2d(fire_grid, modulated_kernel, mode='same', boundary='wrap')
    grid[:, :, 0] += hydra.a * fire_grid[1::]
    grid[:, :, 1] += hydra.b * fire_grid[1::]
    grid[:, :, 2] += hydra.c * fire_grid[1::]
