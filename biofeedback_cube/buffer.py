import colorsys
import random

import numpy as np
from scipy.ndimage import filters
from scipy.ndimage import rotate
from skimage.draw import line_aa


from biofeedback_cube.utils import open_image, sin, cos
from biofeedback_cube import geom


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

    def test_grid(self, t, width=1, weight=1.0):
        v = int(sin(2*t)*self.height)
        color = np.array((0.5, .0, .4))
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

    def draw_line(self, *pts):
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
        self.grid[rr, cc, 1] = val

    def lines(self, t):
        self.draw_line(
            2*np.sin(t) + 0.5,
            2*np.cos(t) + 0.5,
            2*np.sin(t + np.pi) + 0.5,
            2*np.cos(t + np.pi) + 0.5,
        )

    def clear(self):
        self.grid[:] = 0.0

    def fade(self, amt=0.995):
        self.grid[:] *= amt

    def blur(self, sigma=2):
        self.grid[:] = filters.gaussian_filter(self.grid, (sigma, sigma,0))

    def image(self, t, fname, x0=20, y0=15, weight=1.0):
        scale = 0.12  #  0.0 + 0.1*sin(4*t)
        rgba = open_image(fname, scale=scale)
        rgba = rotate(rgba, 20*t)
        im = rgba[:,:,:3]
        alpha = np.expand_dims(rgba[:,:,3], 2)
        h, w = im.shape[:2]
        self.grid[y0:y0+h, x0:x0+w, :] += weight * alpha * im[:, :, :]

    def update(self, t):
        # self.clear()
        self.fade(0.96)
        self.lines(t)
        # self.test_grid(t, width=2, weight=1)
        # self.circle(t, weight=cos(0.5*t))
        # self.image(t, 'heart.png')
        # self.blur(0.7)
        # self.starfield(t)

    def get_grid(self):
        return np.clip(self.buffer[self.jy, self.ix, :], 0, 1)

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