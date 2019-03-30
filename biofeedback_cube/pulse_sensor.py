import asyncio
import logging
import struct

from Adafruit_PureIO.smbus import SMBus
import numpy as np


logger = logging.getLogger(__name__)

DELAY = 1 / 50
PULSE_SENSOR_ADDR = 0x09
try:
    bus = SMBus(1)
except FileNotFoundError:
    logger.warning('failed to init SMBus')

buffer = np.zeros(shape=(int(7 * 86400 / DELAY ), 2), dtype=np.uint16)
idx = 0


def read():
    raw_data = bus.read_bytes(PULSE_SENSOR_ADDR, 2)
    val = struct.unpack('h', raw_data)[0]
    return val


def normalized_read():
    # FIXME: implement circular buffer normalization
    def normalize(x):
        normal = np.clip((x - 350) / 300, 0, 1)
        return normal

    val = read()
    return normalize(val)


def latest():
    return buffer[idx, :]


@asyncio.coroutine
def pulse():
    global idx
    print("collecting heartbeat data . . . ")

    while True:
        value = read()
        buffer[idx, :] = (value, 0)
        yield from asyncio.sleep(DELAY)
        idx += 1


if __name__ == "__main__":
    while True:
        print(read())
