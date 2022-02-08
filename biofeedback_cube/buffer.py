import logging
import operator

import numpy as np
from scipy.ndimage import filters, rotate

from biofeedback_cube.hydra import hydra
from biofeedback_cube.modes import Modes
from biofeedback_cube.fx import std
from biofeedback_cube.fx.fire import fire
from biofeedback_cube.fx.punyty import punyty

logger = logging.getLogger(__name__)

MODE_MAP = {
    Modes.MARIO: std.mario,
    Modes.CIRCLE: std.circle,
    Modes.TEST_GRID: std.test_grid,
    Modes.TV_TEST: std.tv_test,
    Modes.HEART: std.heart,
    Modes.JC: std.jc,
    Modes.STARFIELD: std.starfield,
    Modes.PUNYTY: punyty,
    Modes.PLASMA: std.plasma,
    Modes.PLASMA2: std.plasma2,
    Modes.STROBE: std.strobe,
    Modes.EARLY_FIRE: std.early_fire,
    Modes.FIRE: fire
}

class Buffer():
    """ Holds an array Buffer.buffer of size=size, SxSx4 on which to draw.
    The last channel is (1,R,G,B), so make
    transformation to Dotstar LED format 0xffrrggbb simpler at the expense
    of minor complexity here

    Buffer.get_grid samples the buffer to create an array of the correct size to
    display on an LED array of size (rows,cols). For example Biofeedback cube is 68x8
    and it is evenly sampled from the size=80 buffer by get_grid

    hydra is a class which contains all user interface controls, e.g. position
    of a slider or joystick
    """

    def __init__(self, rows, cols, size=None):
        self.rows = rows
        self.cols = cols

        self.height = size or rows
        self.width = size or rows  # Biofeedback Cube mark I is 68Hx8W

        self.buffer = np.zeros(shape=(self.height, self.width, 4), dtype=np.float64)

    @property
    def grid(self):
        """ grid is a view of the buffer with only 3 channels for color instead of 4 channels including
        the extra 0xff as described in the Buffer docstring. This is an easier canvas to draw upon """
        return self.buffer[:, :, 1:]

    def fade(self, amt=0.8):
        log_amt = np.log10(1 + amt * (10 - 1))
        self.grid[:] *= log_amt

    def blur(self, sigma=2):
        self.grid[:] = filters.gaussian_filter(self.grid, (sigma, sigma,0))

    def bright(self, bright=1.0):
        self.grid[:] *= bright

    def rotate(self, angle: float):
        self.grid[:] = rotate(
            self.grid,
            -180 + angle * 360,
            reshape=False,
            prefilter=True,
            order=3,
            mode='nearest'
        )

    def update(self, t):

        self.fade(hydra.d)
        MODE_MAP[Modes(hydra.mode)](self.grid, t)
        self.rotate(hydra.g)

    def get_grid(self):
        slice_width = self.width // self.cols
        s = slice(0, slice_width * self.cols, slice_width)
        return self.buffer[:, s, :]

