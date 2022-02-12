#!/home/pi/berryconda3/bin/python

import collections
import functools
import logging
import socket
import struct
import time

from Adafruit_PureIO.smbus import SMBus
from pythonosc import udp_client, osc_message_builder


logger = logging.getLogger(__name__)

FREQ = 40
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


_bus = bus()


@functools.lru_cache()
def client():
    host = '10.0.0.255'
    port = 37339
    return udp_client.SimpleUDPClient(host, port, allow_broadcast=True)


_client = client()
_message = osc_message_builder.OscMessageBuilder('/pulse')
_message.add_arg(0.0)
_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
_sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1)
# Enable broadcasting mode
_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
UDP_IP = "10.0.0.255"
UDP_PORT = 37340


def send_osc(value):
    args = (_message._args[0][0], value)
    _message._args[0] = args
    _client.send(_message.build())
    # _client.send_message("/pulse", value)


def send_udp(value):
    message = bytes([int(255*value)])
    _sock.sendto(message, (UDP_IP, UDP_PORT))


def read():
    raw_data = _bus.read_bytes(PULSE_SENSOR_ADDR, 2)
    val = struct.unpack('h', raw_data)[0]
    if val < 0:
        return 0
    return val


def normalized_read():

    val = read()
    buffer.append(val)
    min_val = min(buffer)
    val_range = max(buffer) - min_val

    if val_range:
        normal = ((val - min_val) / val_range)
    else:
        normal = 0.0
    return normal


def main():
    logger.info("collecting heartbeat data . . . ")
    while True:
        value = read() / 1024
        # value = normalized_read()
        # send_osc(value)
        send_udp(value)
        time.sleep(.01)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
