#!/home/pi/berryconda3/bin/python

import collections
import functools
import logging
import struct
import time

from Adafruit_PureIO.smbus import SMBus
import numpy as np
from pythonosc import udp_client

logger = logging.getLogger(__name__)

FREQ = 20
DELAY = 1 / FREQ
BUF_LEN = FREQ * 2
PULSE_SENSOR_ADDR = 0x09

buffer = collections.deque([512]*BUF_LEN, BUF_LEN)

@functools.lru_cache()
def bus():
    try:
        return SMBus(1)
    except FileNotFoundError:
        logger.warning('failed to init SMBus')


@functools.lru_cache()
def client():
    host = '10.0.0.255'
    port = 37339
    return udp_client.SimpleUDPClient(host, port, allow_broadcast=True)


def send_osc(value):
    client().send_message("/pulse", value)


def read():
    raw_data = bus().read_bytes(PULSE_SENSOR_ADDR, 2)
    val = struct.unpack('h', raw_data)[0]
    return val


def normalized_read():

    val = read()
    buffer.append(val)
    min_val = min(buffer)
    val_range = max(buffer) - min_val

    if val_range > 0:
        normal = ((val - min_val) / val_range)
    else:
        normal = 0

    return normal


def main():
    logger.info("collecting heartbeat data . . . ")
    while True:
        value = normalized_read()
        # logger.debug(f'read {value}')
        send_osc(value)
        time.sleep(DELAY)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
