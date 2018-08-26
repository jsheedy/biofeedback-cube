import asyncio
from datetime import datetime
import struct
import time

import numpy as np

from Adafruit_PureIO.smbus import SMBus

# from utils import bytes_to_str

T = 1 / 50
PULSE_SENSOR_ADDR = 0x09
bus = SMBus(1)

buffer = np.zeros(shape=(int(7 * 86400 / T ), 2), dtype=np.uint16)
idx = 0

def read():
	raw_data = bus.read_bytes(PULSE_SENSOR_ADDR, 2)
	val = struct.unpack('h', raw_data)[0]
	return val


def latest():
	return buffer[idx,:]


@asyncio.coroutine
def pulse():
	global idx
	print("collecting heartbeat data . . . ")

	while True:
		value = read()
		buffer[idx,:] = (value, 0)
		yield from asyncio.sleep(T)
		idx += 1


if __name__ == "__main__":
	while True:
		print(read())
