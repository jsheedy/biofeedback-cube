#!/usr/bin/env python

import numpy as np


class Face():

    def __init__(self, rows=68, cols=8):
        self.rows = rows
        self.cols = cols
        self.N = rows * cols
        self.arr = np.zeros(rows * cols * 4, dtype=np.float64)
        self.grid = np.zeros(shape=(rows, cols, 4), dtype=np.float64)

    def test_pattern_lines(self, t):
        v = int((t*self.rows ) % self.rows)
        self.arr[:] = 0
        self.arr[1+v::4*self.rows] = 1.0
        # self.arr[2::4] = 0
        # self.arr[3::4] = 0.0
        return self.arr

    def to_arr(self):
        x = self.grid
        x[:, 0::2, :] = x[::-1, 0::2, :]
        return x.transpose(1, 0, 2).ravel()

    def test_pattern_triangle(self):
        """  """
        self.arr[:] = 0
        self.arr[1::4] = np.linspace(0,.5,self.N)
        self.arr[2::4] = np.linspace(.5,0,self.N)
        return self.arr

    def test_grid(self, t):
        f = 3
        v = int((np.sin(f*t)/2+0.5)*self.rows)
        self.grid[:, :, 1] = 0
        # self.grid[:,:,1:4] *= 0.01
        self.grid[v, :, 2] = .8

    def test_normal_grid(self, t):
        cube = self.grid[:, :, 1:4]
        yy, xx = np.mgrid[0:1:complex(0, self.rows), 0:1:complex(0, self.cols)]

        def sin(x):
            return (np.sin(x) + 1)/2

        def cos(x):
            return (np.cos(x) + 1)/2

        x = .11 + sin(9.5*xx*yy + 2*t)  * cos(8*yy + 4*t) + sin(xx+3.0*t)*cos(yy+2.0*t)
        r = .2 + 0.3 * sin(.2*t)
        g = 0.1 + .2 * sin(t)
        b = 0.3
        cube[:, :, 0] = b*x
        cube[:, :, 1]  = g*x
        cube[:, :, 2] = r*x
        return self.to_arr()

    def anatomecha(self, t):
        cube = self.grid[:, :, 1:4]
        yy, xx = np.mgrid[0:1:complex(0, self.rows), 0:1:complex(0, self.cols)]

        def sin(x):
            return (np.sin(x) + 1)/2

        def cos(x):
            return (np.cos(x) + 1)/2

        blue = np.expand_dims(np.linspace(np.clip(t/20,0,1),np.clip(t/40,0,1),self.rows), 0)
        red = np.expand_dims(np.linspace(np.clip(t/40,0,1),np.clip(t/80,0,1),self.rows), 0)
        green = np.expand_dims(np.linspace(np.clip(t/40,0,1),np.clip(t/80,0,1),self.rows), 0)
        cube[:, :, 0] = 0.1 * blue.T
        if t > 0:
            cube[:, :, 2] = 0.3 * red.T
        cube[:, :, 1] = 0.1 * green.T
        mask = (0.6*(xx-0.5)**2 + (yy-0.1 - sin(0.1*t))**2) < (0.1)
        cube[mask, :] = 0.1

        return self.to_arr()

    def iter_pixels(self, i):
        """ light each pixel in sequence """
        color = ((i // self.N) % 3) + 1
        self.arr[:] = 0
        self.arr[color + (i % self.N)*4] = 1
        return self.arr

    def render(self, t, i):
        # return self.iter_pixels(int(t*300))
        # return self.test_pattern_lines(t)
        # return self.test_pattern_triangle()
        # return self.test_heart(t)
        return self.test_grid(t)
        # return self.test_normal_grid(t)
        # return self.anatomecha(t)

