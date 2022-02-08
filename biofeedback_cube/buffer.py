import colorsys
from functools import partial
import logging
import operator
import random

import numpy as np
from scipy.ndimage import filters

from biofeedback_cube.utils import open_image, sin, cos
from biofeedback_cube.modes import Modes
from biofeedback_cube.fx import std
from biofeedback_cube.fx.fire import fire
from biofeedback_cube.fx.punyty import punyty

logger = logging.getLogger(__name__)


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

    def __init__(self, rows, cols, size=None, hydra=None):
        self.rows = rows
        self.cols = cols

        self.height = size or rows
        self.width = size or rows  # Biofeedback Cube mark I is 68Hx8W

        self.hydra = hydra

        self.buffer = np.zeros(shape=(self.height, self.width, 4), dtype=np.float64)

        self.ix, self.iy = np.meshgrid(
            np.linspace(0, self.width, self.cols, endpoint=False, dtype=np.int32),
            np.linspace(0, self.height, self.rows, endpoint=False, dtype=np.int32)
        )

        self.locals = {
            'layer_op': operator.iadd,
            's': -1
        }

    @property
    def grid(self):
        """ grid is a view of the buffer with only 3 channels for color instead of 4 channels including
        the extra 0xff as described in the Buffer docstring. This is an easier canvas to draw upon """
        return self.buffer[:, :, 1:]

    @property
    def layer_op(self):
        return self.locals['layer_op']

    def fade(self, amt=0.8):
        log_amt = np.log10(1 + amt * (10 - 1))
        self.grid[:] *= log_amt

    def blur(self, sigma=2):
        self.grid[:] = filters.gaussian_filter(self.grid, (sigma, sigma,0))

    def bright(self, bright=1.0):
        self.grid[:] *= bright


    def select_op(self):
        if self.hydra.x < 0.3:
            self.locals['layer_op'] = operator.imul

        elif self.hydra.x > 0.3 and self.hydra.x < 0.6:
            self.locals['layer_op'] = operator.ipow

        else:
            self.locals['layer_op'] = operator.iadd

    def update(self, t):

        mode_map = {
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
            Modes.EARLY_FIRE: std.early_fire
        }

        self.fade(self.hydra.d)
        mode_map[Modes(self.hydra.mode)](self.grid, t)

    def get_grid(self):
        slice_width = self.width // self.cols
        s = slice(0, slice_width * self.cols, slice_width)
        return self.buffer[:, s, :]

    def __keyframes(cols, rows):
        times = np.linspace(0, 1, 5)
        frames = np.zeros((cols, rows, 3, 5))

        frames[:,:,0,0] = 1
        frames[:,:(rows//2),1,1] = 1
        frames[:,(rows//2):,2,2] = 1
        frames[:,:,:,3] = 1
        frames[:,:,1:2,4] = 1
        return times, frames

    def __get_grid(cols, rows, t, joystick):
        # grid = joystick.y*np.random.random((cols,rows,3)) # np.mgrid[100:100] # ds['hgt'][t,state.l]

        times, frames = keyframes(cols, rows)
        idx = int(4*joystick.y)
        grid1 = frames[:,:,:,idx]
        grid2 = frames[:,:,:,idx+1]
        t1 = times[idx]
        t2 = times[idx+1]

        dt = 4 * (joystick.y - idx/4)
        grid = grid1 * (1-dt) + grid2 * (dt)
        print(idx, t1, t2, joystick.y, dt)
        return grid
