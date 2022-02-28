import logging

import numpy as np
from scipy.ndimage import filters, rotate

from biofeedback_cube.fx import std
from biofeedback_cube.fx.cat_jam import jam
from biofeedback_cube.fx.fire import fire
from biofeedback_cube.fx.image import image
from biofeedback_cube.fx.larson import larson
from biofeedback_cube.fx.palette import palette
from biofeedback_cube.fx.punyty import punyty
from biofeedback_cube.fx.punyty import punyty
from biofeedback_cube.hydra import hydra
from biofeedback_cube.modes import Modes

logger = logging.getLogger(__name__)

MODE_MAP = {
    Modes.IMAGE: image,
    Modes.CIRCLE: std.circle,
    Modes.TENT: std.tent,
    Modes.TEST_GRID: std.test_grid,
    Modes.STARFIELD: std.starfield,
    Modes.PUNYTY: punyty,
    Modes.PLASMA: std.plasma,
    Modes.PLASMA2: std.plasma2,
    Modes.STROBE: std.strobe,
    Modes.EARLY_FIRE: std.early_fire,
    Modes.FIRE: fire,
    Modes.PALETTE: palette,
    Modes.LARSON: larson,
    Modes.CATJAM: jam
}


class Buffer():
    """ Holds an array Buffer.buffer of size=size, SxSx4 on which to draw.
    The last channel is (1,R,G,B), so make
    transformation to Dotstar LED format 0xffrrggbb simpler at the expense
    of minor complexity here

    hydra is a class which contains all user interface controls, e.g. position
    of a slider or joystick
    """

    def __init__(self, height, width):

        self.height = height
        self.width = width
        self.buffer = np.zeros(shape=(height, width, 4), dtype=np.float64)

    @property
    def grid(self):
        """ grid is a view of the buffer with only 3 channels for color instead of 4 channels including
        the extra 0xff as described in the Buffer docstring. This is an easier canvas to draw upon """
        return self.buffer[:, :, 1:]

    def fade(self, amt=0.8):
        log_amt = np.log10(1 + amt * (10 - 1))
        self.grid[:] *= log_amt

    def blur(self, sigma: float = 100.0):
        self.grid[:] = filters.gaussian_filter(self.grid, sigma=sigma)
        # self.grid[:] = filters.sobel(self.grid)

    def rotate(self, angle: float):
        if angle == 0.0:
            return
        self.grid[:] = rotate(
            # hack to stretch 68x8 square for rotation
            np.repeat(self.grid, 8, axis=1),
            0 + angle * 360,
            reshape=False,
            prefilter=True,
            order=3,
            mode='nearest'
        )[:, ::8, :]

    def update(self, t):

        self.fade(hydra.d)
        for mode in hydra.modes:
            MODE_MAP[mode](self.grid, t)
        self.rotate(hydra.h)
