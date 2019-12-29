#!/usr/bin/env python

import colorsys
import time

import numpy as np

from dotstar import Adafruit_DotStar


numpixels = 1 # Number of LEDs in strip

strip = Adafruit_DotStar(32000000)
strip.begin()

arr = np.full(numpixels*4, 255, dtype=np.uint8)

r = arr[1:-1:4]
g = arr[2:-1:4]
b = arr[3:3+numpixels*4:4]

g[:]=0
while True:
    strip.show(arr.astype(np.uint8).tostring())
