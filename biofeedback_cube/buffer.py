import colorsys
import logging
import math
import operator
import random

import numpy as np
from punyty.vector import Vector3
from punyty.objects import Cube
from punyty.renderers import ArrayRenderer
from punyty.scene import Scene
from scipy.ndimage import filters

from biofeedback_cube.utils import open_image, sin, cos


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

        self.yy, self.xx = np.mgrid[0:1:complex(0, self.height), 0:1:complex(0, self.width)]

        self.ix, self.iy = np.meshgrid(
            np.linspace(0, self.width, self.cols, endpoint=False, dtype=np.int32),
            np.linspace(0, self.height, self.rows, endpoint=False, dtype=np.int32)
        )
        self.iix = np.arange(self.width, dtype=np.int32)
        self.iiy = np.arange(self.height, dtype=np.int32)

        self.locals = {
            'layer_op': operator.iadd,
            's': -1
        }

        # for punytty mode, should isolate this
        self.scene = Scene()
        self.cube = Cube(color=Vector3(1, 0.8, 0.7), position=Vector3(-.35, 0, 1.3))
        self.scene.add_object(self.cube)
        self.renderer = ArrayRenderer(
            target_array=self.buffer[:, :, 1:],
            draw_edges=False,
            draw_wireframe=False
        )

    @property
    def grid(self):
        """ grid is a view of the buffer with only 3 channels for color instead of 4 channels including
        the extra 0xff as described in the Buffer docstring. This is an easier canvas to draw upon """
        return self.buffer[:, :, 1:]

    @property
    def layer_op(self):
        return self.locals['layer_op']

    def hydra_fresh(self, t):
        """ return boolean whether hydra has been updated recently """
        dt = t - self.hydra.last_update
        return dt < .3

    def punyty(self, t):

        if self.hydra.d < 0.2:
            self.cube.rotate(Vector3(-3+self.hydra.a*6, -3+self.hydra.b*6, -3+self.hydra.c*6))
        else:
            self.cube.rotate(Vector3(math.sin(.5*t), math.sin(0.53*t), math.cos(0.45*t)))

        self.cube.color = Vector3(self.hydra.a, self.hydra.b, self.hydra.c)
        # self.cube.color = Vector3(sin(.1*t), .1 + .9*cos(.05*t), sin(0.1*t)*cos(0.05*t))
        # self.cube.position = Vector3(-.350, 0.5*math.sin(t/2), 1.3 + 0.3 * math.sin(t/3))
        # self.cube.position = Vector3(sin(t), cos(t), 25)
        self.renderer.render(self.scene)

    def starfield(self, t):
        # marker = int(t*5)
        # if marker > self.locals['s']:
            # self.locals['s'] = marker
        for i in range(int(30*self.hydra.x)):
            y = random.randint(0, self.height-1)
            x = random.randint(0, self.width-1)
            self.grid[y, x, :] = random.random(), random.random(), random.random() 
            # self.grid[y, x, :] = colorsys.hsv_to_rgb(random.random(), 1, 1)

    def test_grid(self, t, width=1, weight=1.0):
        if self.hydra_fresh(t):
            y = int((self.height-1) * self.hydra.a)
        else:
            f = (self.hydra.b / .5) ** 2
            y = int(sin(f*t)*(self.height-1))

        h = sin(.2*t)
        s = .5 + .5*cos(.1*t)
        v = .5 + 0.5*cos(t)*sin(t)
        color = colorsys.hsv_to_rgb(h, s, v)
        self.grid[y, :, :] += color

    def pulse_line(self, t, width=2):
        y = int((self.height-1) * self.hydra.pulse)

        h = sin(.2*t)
        s = .5 + .5*cos(.1*t)
        v = .5 + 0.5*cos(t)*sin(t)
        color = colorsys.hsv_to_rgb(h, s, v)

        self.grid[y, :, :] += color


    def __sunrise(self, t):
        blue = np.expand_dims(np.linspace(np.clip(t/20,0,1), np.clip(t/40,0,1), self.width), 0)
        red = np.expand_dims(np.linspace(np.clip(t/40,0,1), np.clip(t/80,0,1), self.width), 0)
        green = np.expand_dims(np.linspace(np.clip(t/40,0,1), np.clip(t/80,0,1), self.width), 0)
        self.grid[:, :, 0] = blue

    def circle(self, t, color=(.7, .4, .2), weight=1.0):
        radius = 0.05

        if self.hydra_fresh(t):
            y = self.hydra.y
            x = 1-self.hydra.x
        else:
            y = 0.25 + 0.5*sin(0.5*t)
            x = 0.25 + 0.5*cos(0.501*t)

        color = (self.hydra.a, self.hydra.b, self.hydra.c)
        mask = ((self.xx-x)**2 + (self.yy - y)**2) < radius
        self.grid[mask, :] += weight * np.array(color)

    def tent(self, t, color=(.7, .2, .4), weight=1.0):
        """ similar to a circle but like a circus tent """
        r = 0.1
        x = self.hydra.x
        y = self.hydra.y

        tent = np.clip(1-np.sqrt((r*(self.xx-x))**2 + (r*(self.yy-y))**2), 0, 1)
        r, g, b = color

        # self.grid[:, :, 0] = self.layer_op(self.grid[:, :, 0], weight * r * tent)
        # self.grid[:, :, 1] = self.layer_op(self.grid[:, :, 1], weight * g * tent)
        # self.grid[:, :, 2] = self.layer_op(self.grid[:, :, 2], weight * b * tent)
        self.grid[:, :, 0] = weight * r * tent
        self.grid[:, :, 1] = weight * g * tent
        self.grid[:, :, 2] = weight * b * tent

    def lines(self, t):
        rgb = (0.2, 0.6, 0.8)
        f = 00.8
        r = 0.9
        pts = (
            int(self.width * (r*np.sin(f*t) + 0.5)),
            int(self.height * (r*np.cos(f*t) + 0.5)),
            int(self.width * (r*np.sin(f*t + np.pi) + 0.5)),
            int(self.height * (r*np.cos(f*t + np.pi) + 0.5)),
        )
        self.renderer.draw_line(pts, rgb)

    def hydra_line(self, t):
        rgb = (self.hydra.a, self.hydra.b, self.hydra.c)
        x = self.hydra.x
        y = self.hydra.y
        pts = (
            0, 0, int(self.width*y), int(self.height*x)
        )
        self.renderer.draw_line(pts, rgb)

    def clear(self, rgb):
        self.grid[:] = rgb
        # self.grid[:, :, :] = self.layer_op(self.grid[:, :, :], rgb)

    def fade(self, amt=0.8):
        self.grid[:] *= amt

    def blur(self, sigma=2):
        self.grid[:] = filters.gaussian_filter(self.grid, (sigma, sigma,0))

    def bright(self, bright=1.0):
        self.grid[:] *= bright

    def image(self, t, fname, scale=1.0):

        if self.hydra_fresh(t):
            x0 = int(self.width * self.hydra.x)
            y0 = int(self.height * self.hydra.y)
        else:
            y0 = int(30*sin(t))
            x0 = int(30*sin(t))

        rgba = open_image(fname, scale=scale)
        im = rgba[:, :, :3]

        h, w = im.shape[:2]

        x_i = np.take(self.iix, range(x0, x0+w), mode='wrap')
        y_i = np.take(self.iiy, range(y0, y0+h), mode='wrap')

        xx_i, yy_i = np.meshgrid(x_i, y_i, sparse=True)

        self.grid[yy_i, xx_i, :] = self.layer_op(self.grid[yy_i, xx_i, :], im)

    def select_op(self):
        if self.hydra.x < 0.3:
            self.locals['layer_op'] = operator.imul

        elif self.hydra.x > 0.3 and self.hydra.x < 0.6:
            self.locals['layer_op'] = operator.ipow

        else:
            self.locals['layer_op'] = operator.iadd

    def update(self, t):
        # self.select_op()
        self.fade(self.hydra.d)
        # self.clear((0.08*sin(t), 0.08*cos(t), .01))
        # self.lines(t)
        if self.hydra.mode == 0:
            self.tent(t, weight=0.4)

        elif self.hydra.mode == 1:
            self.hydra_line(t)

        elif self.hydra.mode == 2:
            self.circle(t)

        elif self.hydra.mode == 3:
            self.test_grid(t, width=2)

        elif self.hydra.mode == 4:
            self.pulse_line(t, width=2)

        elif self.hydra.mode == 5:
            self.image(t, 'heart.png', scale=0.1)

        elif self.hydra.mode == 6:
            self.image(t, 'E.png', scale=0.2)

        elif self.hydra.mode == 7:
            self.starfield(t)

        elif self.hydra.mode == 8:
            self.punyty(t)

        # self.blur(1.2)
        # self.bright(0.99)

    def get_grid(self):
        slice_width = self.width // self.cols
        s = slice(0, slice_width * self.cols, slice_width)
        return self.buffer[:, s, :]
        # return self.buffer[self.iy, self.ix, :]
        # return np.clip(self.buffer[self.iy, self.ix, :], 0, 1)

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
