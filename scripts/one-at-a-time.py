#!/usr/bin/env python

import colorsys
import time

import numpy as np

from dotstar import Adafruit_DotStar


numpixels = 68*8*1 # Number of LEDs in strip

strip    = Adafruit_DotStar()
strip.begin()

arr = np.full(numpixels*4, 255, dtype=np.float32)

r = arr[1:-1:4]
g = arr[2:-1:4]
b = arr[3:3+numpixels*4:4]

while True:
    for c in (0, 1, 2):
        for i in range(0,numpixels):
            r[:] *= 0.92
            g[:] *= 0.92
            b[:] *= 0.90
            if c == 0:
                r[i] = 255
            if c == 1:
                g[i] = 255
            elif c == 2:
                b[i] = 255
            strip.show(arr.astype(np.uint8).tostring())
            time.sleep(0.01)
