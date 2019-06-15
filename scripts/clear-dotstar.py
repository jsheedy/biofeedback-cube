#!/usr/bin/env python

import colorsys
import time

import numpy as np

from dotstar import Adafruit_DotStar


numpixels = 544*1 # Number of LEDs in strip

strip    = Adafruit_DotStar()
strip.begin()

# gamma = bytearray(256)
# for i in range(256):
    # gamma[i] = int(pow(float(i) / 255.0, 2.7) * 255.0 + 0.5)

gamma = [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
    1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
    2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
    5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
   10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
   17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
   25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
   37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
   51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
   69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
   90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
  115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
  144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
  177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
  215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255]

arr = np.zeros(numpixels*4, dtype=np.float32)
# arr = np.zeros(numpixels*4, dtype=np.byte)
arr[0:-1:4] = 0xff
strip.show(arr.tostring())

t = np.arange(0,numpixels, dtype=np.float64)

A = 0.05
w = 0.5

for phase in np.arange(0,1,0.0005):
	r,g,b = colorsys.hsv_to_rgb(phase, 1, 1)
	arr[1:-1:4] = gamma[int(255*b)] * (A*np.sin(-2*w*t+2*np.pi*phase)+A)/2
	arr[2:-1:4] = gamma[int(255*g)] * (A*np.sin(w*t+2*np.pi*phase)+A)/2
	arr[3:3+numpixels*4:4] = gamma[int(255*r)] * (A*np.sin(w*t+9*phase)+A)/2

	strip.show(arr.astype(np.uint8).tostring())
