#!/usr/bin/env python

import argparse
import asyncio

import numpy as np

from pythonosc import udp_client

import pulse_sensor

SAMPLING_DELAY = 1/20

client = udp_client.SimpleUDPClient('192.168.0.255', 37337, allow_broadcast=True)
# client = udp_client.SimpleUDPClient('localhost', 37337)

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("--ip", default="0.0.0.0", help="The ip to listen on")
	args = parser.parse_args()
	return args

def normalize(x):
	normal = np.clip((x - 350) / 300 , 0, 1);
	return normal
	
# async def pulse():
@asyncio.coroutine
def pulse():
	while True:
		x = pulse_sensor.read()
		# x = pulse_sensor.latest()
		print(x)
		# x = x[0]
		client.send_message("/pulse", normalize(x))
		yield from asyncio.sleep(SAMPLING_DELAY)
		# await asyncio.sleep(SAMPLING_DELAY)


def main():
	args = parse_args()
	loop = asyncio.get_event_loop()

	asyncio.async(pulse())
	# asyncio.async(pulse_sensor.pulse())
	# loop.call_soon(pulse, loop)

	loop.run_forever()

if __name__ == "__main__":
	main()
