#!/usr/bin/env python

import argparse
import asyncio
import colorsys
from datetime import datetime, timedelta
import time

import numpy as np

from pythonosc import dispatcher
from pythonosc import osc_server

from dotstar import Adafruit_DotStar


numpixels = 144*1 # Number of LEDs in strip
IDLE_TIME = 2

strip    = Adafruit_DotStar()
# strip    = Adafruit_DotStar(32000000)
strip.begin()           # Initialize pins for output

arr = np.zeros(numpixels*4, dtype=np.byte)
arr[0:-1:4] = 0xff

t = np.arange(0,numpixels, dtype=np.float64)

last_osc = datetime.now() - timedelta(seconds=IDLE_TIME)

@asyncio.coroutine
def looper():

	A = .05
	phase = 0

	while True: 
		if (datetime.now() - last_osc) > timedelta(seconds=IDLE_TIME):
			phase += .01 
			r,g,b = colorsys.hsv_to_rgb(phase, 1, 1)
			arr[1:-1:4] = b * (A*np.sin(t+5*phase)+A)/2*255
			arr[2:-1:4] = g * (A*np.sin(t+6*phase)+A)/2*255
			arr[3:3+numpixels*4:4] = r * (A*np.sin(t+phase)+A)/2*255 
			strip.show(arr.tostring())
		yield from asyncio.sleep(.02)


i = 0

def meter(arr, value, r=0, g=1, b=0):

	meter = np.zeros(numpixels, dtype=np.uint8)
	idx = int(value*numpixels)
	meter[:idx] = 255 * value
	
	# clear
	arr[1:-1:4] = 0
	arr[2:-1:4] = 0
	arr[3:-1:4] = 0

	# arr[1::4] = meter
	# arr[2::4] = meter
	arr[3::4] = meter

	return arr.tostring()


def osc_handler(addr, value, **kwargs):
	global last_osc
	global i
	last_osc = datetime.now()
	i += 1
	if i % 50 == 0:
		print(" ".join((addr, str(value))))
	
	byte_str = meter(arr, value)

	strip.show(byte_str)


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument("--ip", default="0.0.0.0", help="The ip to listen on")
	parser.add_argument("--port", type=int, default=37337, help="The port to listen on")
	args = parser.parse_args()

	loop = asyncio.get_event_loop()

	asyncio.async(looper(), loop=loop)
	# asyncio.ensure_future(looper(), loop=loop)

	dsp = dispatcher.Dispatcher()
	# dsp.map("/pulse", print)
	dsp.map("/pulse", osc_handler)
	server = osc_server.AsyncIOOSCUDPServer((args.ip, args.port), dsp, loop)
	server.serve()
	
	loop.run_forever()


if __name__ == "__main__":
	main()
