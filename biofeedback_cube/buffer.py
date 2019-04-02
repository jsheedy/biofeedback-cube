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
        self.height = 100
        self.width = 100
        self.yy, self.xx = np.mgrid[0:1:complex(0, self.height), 0:1:complex(0, self.width)]

        self.ix, self.jy = np.meshgrid(
            np.linspace(0, self.width, self.cols, endpoint=False, dtype=np.int32),
            np.linspace(0, self.height, self.rows, endpoint=False, dtype=np.int32)
        )

        self.locals = {
            'buffer': np.zeros(shape=(self.height, self.width, 4), dtype=np.float64),
            's': -1
        }

    @property
    def grid(self):
        return self.buffer[:, :, 1:]

    @property
    def buffer(self):
        return self.locals['buffer']

    def starfield(self, t):
        marker = int(t*5)
        if marker > self.locals['s']:
            self.locals['s'] = marker
            y = random.randint(0, self.height-1)
            x = random.randint(0, self.width-1)
            self.grid[y, x, :] = colorsys.hsv_to_rgb(random.random(), 1, 1)

    def test_grid(self, t):
        v = int(sin(2*t)*self.height)
        color = (0.5, .0, .4)
        width = 10
        self.grid[v:v+width, :, :] = color

    def __sunrise(self, t):
        blue = np.expand_dims(np.linspace(np.clip(t/20,0,1), np.clip(t/40,0,1), self.width), 0)
        red = np.expand_dims(np.linspace(np.clip(t/40,0,1), np.clip(t/80,0,1), self.width), 0)
        green = np.expand_dims(np.linspace(np.clip(t/40,0,1), np.clip(t/80,0,1), self.width), 0)
        self.grid[:, :, 0] = blue

    def circle(self, t, color=(0, .2, 1.0)):
        radius = 0.3**2
        y_off = 0.25 + 0.5*sin(1*t)
        x_off = 0.25 + 0.5*cos(1.1*t)
        mask = ((self.xx-x_off)**2 + (self.yy - y_off)**2) < radius
        self.grid[mask, :] = color

    def clear(self):
        self.grid[:] = 0.0

    def fade(self, amt=0.995):
        self.grid[:] *= amt

    def update(self, t):
        # self.clear()
        self.fade(0.93)
        self.test_grid(t)
        self.circle(t)
        # self.starfield(t)

    def get_grid(self):
        return self.buffer[self.jy, self.ix, :]

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