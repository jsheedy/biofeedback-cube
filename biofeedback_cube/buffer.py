import logging
import time

import numpy as np
from scipy.ndimage import filters, rotate

from .config import HEIGHT, WIDTH
from .fx import std
from .fx.cat_jam import jam
from .fx.fire import fire
from .fx.image import image
from .fx.larson import larson
from .fx.midi import midi
from .fx.palette import palette
from .fx.plasma3 import plasma3
from .fx.punyty import punyty
from .hydra import hydra
from .modes import Modes

logger = logging.getLogger(__name__)

MODE_MAP = {
    Modes.IMAGE: image,
    Modes.CONE: std.cone,
    Modes.TEST_GRID: std.test_grid,
    Modes.STARFIELD: std.starfield,
    Modes.PUNYTY: punyty,
    Modes.PLASMA: std.plasma,
    Modes.PLASMA2: std.plasma2,
    Modes.PLASMA3: plasma3,
    Modes.STROBE: std.strobe,
    Modes.EARLY_FIRE: std.early_fire,
    Modes.FIRE: fire,
    Modes.PALETTE: palette,
    Modes.LARSON: larson,
    Modes.CATJAM: jam,
    Modes.MIDI: midi
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
        self.frame_number = 0
        self.height = height
        self.width = width
        self.buffer = np.zeros(shape=(height, width, 4), dtype=np.float32)
        self.t0 = time.time()
        self.t1 = time.time()

    @property
    def grid(self):
        """ grid is a view of the buffer with only 3 channels for color instead of 4 channels including
        the extra 0xff as described in the Buffer docstring. This is an easier canvas to draw upon """
        return self.buffer[:, :, 1:]

    def fps(self):
        NFRAMES = 200
        if self.frame_number % NFRAMES == 1:
            delta = self.t - self.t1
            self.t1 = self.t
            fps = NFRAMES / delta
            logger.debug(f'FPS: {fps:.2f}')

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

    def update(self):
        self.t = time.time() - self.t0
        self.frame_number += 1

        self.fade(hydra.d)
        for mode in hydra.modes:
            MODE_MAP[mode](self.grid, self.t)
        self.rotate(hydra.h)

        self.fps()


buffer = Buffer(HEIGHT, WIDTH)
