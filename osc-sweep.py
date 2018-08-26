#!/usr/bin/env python

import asyncio

import numpy as np

from pythonosc import udp_client

client = udp_client.SimpleUDPClient('192.168.0.255', 37337, allow_broadcast=True)

@asyncio.coroutine
def sweep():
	N = 100
	vals = tuple(map(lambda x: x/N, range(0,N)))
	while True:
		for x in vals + vals[::-1]:
			client.send_message("/pulse", 0.5)
			yield from asyncio.sleep(0.5)


def main():
	loop = asyncio.get_event_loop()
	asyncio.async(sweep())
	loop.run_forever()

if __name__ == "__main__":
	main()
