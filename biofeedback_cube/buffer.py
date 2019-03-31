import colorsys
import random

import numpy as np
from scipy.ndimage import zoom

from biofeedback_cube.utils import sin, cos


class Buffer():
	""" buffer is size WxHx4. The last channel is (1,R,G,B), so make
	transformation to Dotstar LED format 0xffrrggbb simpler as expense
	of minor complexity here """
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.locals = {
            'grid': np.zeros(shape=(rows, cols, 4), dtype=np.float64),
            's': -1
        }
        self.scale = 10
        self.height = rows*10
        self.width = cols*10
        self.buffer = np.zeros(shape=(self.height, self.width, 4))

    def _get_grid(self, t):
        grid = self.locals['grid']
        marker = int(t*5)
        if marker > self.locals['s']:
            self.locals['s'] = marker
            y = random.randint(0, self.rows-1)
            x = random.randint(0, self.cols-1)
            grid[y, x, 1:] = colorsys.hsv_to_rgb(random.random(), 1, 1)

        grid *= 0.995
        return grid

    def update(self, t):
        v = int(sin(2*t)*self.height)
        self.buffer[:, :, :] = 0.0
        self.buffer[v:v+20, :, 3] = 1.0

    def get_grid(self):
        # return self.buffer[::self.scale, ::self.scale, :]
        return zoom(self.buffer, (0.1, 0.1, 1.0))


