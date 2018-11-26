#!/usr/bin/env python

import colorsys
from datetime import datetime, timedelta
import time

import numpy as np

from dotstar import Adafruit_DotStar

def as_uint8(arr, gamma=2.4):

	gamma_corrected = np.clip(arr, 0, 1) ** gamma
	u8 = (gamma_corrected * 255.0).astype(np.uint8)
	u8[0::4] = 0xff  # dotstar format is (0xff,r,g,b)
	return u8.tobytes()

	# interpolate from buffer resolution to device resolution
	# r = np.interp(self.device_x, self.buffer_x, buff[:,0]) * 255
	# g = np.interp(self.device_x, self.buffer_x, buff[:,1]) * 255
	# b = np.interp(self.device_x, self.buffer_x, buff[:,2]) * 255

	# device_buffer = np.vstack((r,g,b)).T
	# return device_buffer.astype(np.uint8).tobytes()


class Face():
	def __init__(self, rows=68, cols=8):
		self.rows = rows
		self.cols = cols
		self.N = rows * cols
		self.arr = np.ones(rows * cols * 4, dtype=np.float64)
		# arr[0:-1:4] = 0xff

	def waves(self, t):
		phase = 0.2
		A = 1.0
		r,g,b = colorsys.hsv_to_rgb(phase, 1, 1)

		self.arr[1:-1:4] = b * (A*np.sin(t+5*phase)+A)/2
		self.arr[2:-1:4] = g * (A*np.sin(t+6*phase)+A)/2
		self.arr[3:3+self.rows*self.cols*4:4] = r * (A*np.sin(t+phase)+A)/2

	def test_pattern_lines(self, t):
		v = int((t*self.rows ) % self.rows)
		self.arr[:] = 0
		self.arr[1+v::4*self.rows] = 0.5
		# self.arr[2::4] = 0
		# self.arr[3::4] = 0.0
		return self.arr

	def iter_pixels(self, i):
		""" light each pixel in sequence """
		color = ((i // self.N) % 3) + 1
		self.arr[:] = 0	
		self.arr[color + (i%self.N)*4] = 1
		return self.arr
		
	def render(self, t, i):
		return self.iter_pixels(int(t*300))
		# return self.test_pattern_lines(t)


def main():
	strip  = Adafruit_DotStar()
	strip.begin()
	face = Face()
	t0 = time.time()
	i = 0
	while True:
		t = time.time() - t0	
		arr = face.render(t=t, i=i)
		i += 1
		arr_bytes = as_uint8(arr)
		# print(arr_bytes)
		strip.show(arr_bytes)
		# time.sleep(.005)


if __name__ == "__main__":
	main()
