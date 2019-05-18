import colorsys
import logging
import operator
import random

import numpy as np
from punyty.vector import Vector3
from punyty.objects import Cube
from punyty.renderers import ArrayRenderer
from punyty.scene import Scene
from scipy.ndimage import filters
from scipy.ndimage import rotate
from skimage.draw import line_aa

from biofeedback_cube.utils import open_image, sin, cos
from biofeedback_cube import geom


logger = logging.getLogger(__name__)


class Buffer():
    """ buffer is size WxHx4. The last channel is (1,R,G,B), so make
    transformation to Dotstar LED format 0xffrrggbb simpler as expense
    of minor complexity here """

    def __init__(self, rows, cols, hydra=None):
        self.rows = rows
        self.cols = cols
        size = 200
        self.height = size
        self.width = size
        self.hydra = hydra
        self.yy, self.xx = np.mgrid[0:1:complex(0, self.height), 0:1:complex(0, self.width)]

        self.ix, self.iy = np.meshgrid(
            np.linspace(0, self.width, self.cols, endpoint=False, dtype=np.int32),
            np.linspace(0, self.height, self.rows, endpoint=False, dtype=np.int32)
        )
        self.iix = np.arange(self.width, dtype=np.int32)
        self.iiy = np.arange(self.height, dtype=np.int32)

        self.buffer = np.zeros(shape=(self.height, self.width, 4), dtype=np.float64)
        self.locals = {
            'layer_op': operator.iadd,
            's': -1
        }
        self.scene = Scene()
        self.cube = Cube()
        self.scene.add_object(self.cube)
        self.renderer = ArrayRenderer(target_array=self.buffer[:, :, 1:])

    @property
    def grid(self):
        return self.buffer[:, :, 1:]

    @property
    def layer_op(self):
        return self.locals['layer_op']

    def punyty(self, t):

        self.cube.rotate(Vector3(self.hydra.x*6, t / 4, self.hydra.y*6))
        self.cube.position = Vector3(0, 0, -5 + self.hydra.z*10)
        self.renderer.render(self.scene, draw_polys=True)

    def starfield(self, t):
        marker = int(t*5)
        if marker > self.locals['s']:
            self.locals['s'] = marker
            y = random.randint(0, self.height-1)
            x = random.randint(0, self.width-1)
            self.grid[y, x, :] = colorsys.hsv_to_rgb(random.random(), 1, 1)

    def test_grid(self, t, width=1, weight=1.0):
        v = int(sin(0.8*t)*self.height)
        color = np.array((0.5, .1, 0.1*sin(0.2*t)))
        self.grid[v:v+width, :, :] += weight * color

    def __sunrise(self, t):
        blue = np.expand_dims(np.linspace(np.clip(t/20,0,1), np.clip(t/40,0,1), self.width), 0)
        red = np.expand_dims(np.linspace(np.clip(t/40,0,1), np.clip(t/80,0,1), self.width), 0)
        green = np.expand_dims(np.linspace(np.clip(t/40,0,1), np.clip(t/80,0,1), self.width), 0)
        self.grid[:, :, 0] = blue

    def circle(self, t, color=(0, .2, 1.0), weight=1.0):
        radius = 0.3**2
        y_off = 0.25 + 0.5*sin(1*t)
        x_off = 0.25 + 0.5*cos(1.1*t)
        mask = ((self.xx-x_off)**2 + (self.yy - y_off)**2) < radius
        self.grid[mask, :] += weight * np.array(color)

    def tent(self, t, color=(.7, .2, .4), weight=1.0):
        """ similar to a circle but like a circus tent """
        r = 1*(sin(0.3*t)+2)
        tent = np.clip(1-np.sqrt((r*(self.xx-0.5))**2+ (r*(self.yy-0.5))**2), 0, 1)
        r,g,b = color
        self.grid[:, :, 0] = self.layer_op(self.grid[:, :, 0], weight * r * tent)
        self.grid[:, :, 1] = self.layer_op(self.grid[:, :, 1], weight * sin(t) * tent)
        self.grid[:, :, 2] = self.layer_op(self.grid[:, :, 2], weight * b * tent)

    def draw_line(self, rgb, pts):
        assert len(pts) == 4
        # if points lie outside uv, find the intersection points
        intersections = geom.line_intersects_uv(*pts)
        if len(intersections) == 2:
            x0, y0 = intersections[0]
            x1, y1 = intersections[1]
        elif len(intersections) == 1:
            x0, y0 = intersections[0]
            if geom.point_in_uv(*pts[:2]):
                x1, y1 = pts[:2]
            elif geom.point_in_uv(*pts[2:]):
                x1, y1 = pts[2:]
            else:
                return
        elif geom.point_in_uv(*pts[:2]) and geom.point_in_uv(*pts[2:]):
            x0, y0, x1, y1 = pts
        else:
            return

        ix0 = int(x0 * (self.width-1))
        iy0 = int(y0 * (self.height-1))
        ix1 = int(x1 * (self.width-1))
        iy1 = int(y1 * (self.height-1))
        rr, cc, val = line_aa(ix0, iy0, ix1, iy1)
        r,g,b = rgb
        self.grid[rr, cc, 0] += r * val
        self.grid[rr, cc, 1] += g * val
        self.grid[rr, cc, 2] += b * val

    def lines(self, t):
        rgb = (0.2, 0.6, 0.8)
        f = 00.4
        r = 0.9
        pts = (
            r*np.sin(f*t) + 0.5,
            r*np.cos(f*t) + 0.5,
            r*np.sin(f*t + np.pi) + 0.5,
            r*np.cos(f*t + np.pi) + 0.5,
        )
        self.draw_line(rgb, pts)

    def hydra_line(self, t):
        rgb = (0.1, 0.2, 0.9)
        y = self.hydra.pulse
        pts = (
            y, 0, y, 1
        )
        self.draw_line(rgb, pts)

    def clear(self):
        self.grid[:] = 0.0

    def fade(self, amt=0.995):
        self.grid[:] *= amt

    def blur(self, sigma=2):
        self.grid[:] = filters.gaussian_filter(self.grid, (sigma, sigma,0))

    def bright(self, bright=1.0):
        self.grid[:] *= bright

    def image(self, t, fname, x0=0, y0=15, weight=1.0, scale=1.0):
        rgba = open_image(fname, scale=scale)
        # rgba = rotate(rgba, np.pi/2)

        y0 = int(30*t)
        x0 = int(30*t)
        # y0 = int(sin(99*t)*self.height)
        im = rgba[:, :, :3]
        # alpha = np.expand_dims(rgba[:, :, 3], 2)
        alpha = 1.0
        h, w = im.shape[:2]

        x_i = np.take(self.iix, range(x0, x0+w), mode='wrap')
        y_i = np.take(self.iiy, range(y0, y0+h), mode='wrap')

        xx_i, yy_i = np.meshgrid(x_i, y_i, sparse=True)

        y = weight * alpha * im
        self.grid[yy_i, xx_i, :] = self.layer_op(self.grid[yy_i, xx_i, :], y)
        # blit[:] = y[:]

    def select_op(self):
        if self.hydra.x < 0.3:
            self.locals['layer_op'] = operator.imul

        elif self.hydra.x > 0.3 and self.hydra.x < 0.6:
            self.locals['layer_op'] = operator.ipow

        else:
            self.locals['layer_op'] = operator.iadd

    def update(self, t):
        # self.select_op()
        # self.clear()
        self.fade(0.90)
        self.punyty(t)
        # self.lines(t)
        # self.tent(t, weight=0.4)
        # self.test_grid(t, width=2, weight=1)
        # self.hydra_line(t)
        # self.circle(t, weight=cos(0.5*t))
        # self.image(t, 'lena.png', scale=0.37)
        # self.image(t, 'heart.png', scale=0.4)
        # self.image(t, 'E.png')
        self.blur(1.2)
        # self.bright(0.99)
        # self.starfield(t)

    def get_grid(self):
        return np.clip(self.buffer[self.iy, self.ix, :], 0, 1)

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
