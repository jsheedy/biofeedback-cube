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
        # self.height = rows * self.scale
        # self.width = cols * self.scale
        # self.buffer = np.zeros(shape=(self.height, self.width, 4))
        self.height = rows
        self.width = rows
        self.hscale = self.cols / self.width
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

    def test_grid(self, t):
        v = int(sin(2*t)*self.height)
        self.buffer[:, :, :] = 0.0
        self.buffer[v:v+20, :, 3] = 1.0

    def circle(self, t):
        cube = self.buffer[:, :, 1:4]
        yy, xx = np.mgrid[0:1:complex(0, self.height), 0:1:complex(0, self.width)]

        # blue = np.expand_dims(np.linspace(np.clip(t/20,0,1),np.clip(t/40,0,1),self.rows), 0)
        # red = np.expand_dims(np.linspace(np.clip(t/40,0,1),np.clip(t/80,0,1),self.rows), 0)
        # green = np.expand_dims(np.linspace(np.clip(t/40,0,1),np.clip(t/80,0,1),self.rows), 0)

        # cube[:, :, 0] = 0.1 * blue.T
        # if t > 0:
        #     cube[:, :, 2] = 0.3 * red.T
        # cube[:, :, 1] = 0.1 * green.T

        radius = 0.3**2
        y_off = 0.25 + 0.5*sin(2*t)
        x_off = 0.25 + 0.5*cos(2*t)
        mask = ((xx-x_off)**2 + (yy - y_off)**2) < radius
        cube[mask, 2] = 1

    def clear(self):
        self.buffer[:, :, 1:] = 0.0

    def update(self, t):
        self.clear()
        # self.test_grid(t)
        self.circle(t)

    def get_grid(self):
        # return self.buffer[::self.scale, ::self.scale, :]
        return zoom(self.buffer, (1, self.hscale, 1))

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