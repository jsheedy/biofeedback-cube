#!/usr/bin/env python

import argparse
import asyncio
import logging
import random
import time

import numpy as np
from pythonosc import dispatcher, udp_client
from pythonosc.osc_server import AsyncIOOSCUDPServer

from biofeedback_cube import pulse_sensor
from biofeedback_cube import display

logger = logging.getLogger(__name__)

SAMPLING_DELAY = 1/20

osc_queue = []


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=37337, help="The port to listen on")
    args = parser.parse_args()
    return args


@asyncio.coroutine
def main_loop(coros):
    done, _pending = yield from asyncio.wait(coros, return_when=asyncio.FIRST_EXCEPTION)
    for t in done:
        if t.exception():
            logger.exception(f'task exception {t}')
            raise t.exception()


@asyncio.coroutine
def osc_server(host, port):
    def osc_handler(addr, value, **kwargs):
        logger.info(" ".join((addr, str(value))))
        osc_queue.append(value)

    dsp = dispatcher.Dispatcher()
    dsp.map("/pulse", osc_handler)
    loop = asyncio.get_event_loop()
    server = AsyncIOOSCUDPServer((host, port), dsp, loop)
    server.create_serve_endpoint()


rows = 68
cols = 8


@asyncio.coroutine
def render():
    t0 = time.time()
    grid = np.zeros(shape=(rows, cols, 4), dtype=np.float64)
    s = -1
    while True:
        t = time.time() - t0
        if int(t) > s:
            s = int(t)
            y = random.randint(0, rows-1)
            x = random.randint(0, cols-1)
            grid[y, x, 1] = 1.0

        grid *= 0.995
        display.draw(grid)
        yield from asyncio.sleep(0.05)


@asyncio.coroutine
def pulse_to_osc(host, port):

    # osc_client = udp_client.SimpleUDPClient('192.168.0.255', 37337, allow_broadcast=True)
    osc_client = udp_client.SimpleUDPClient(host, property)

    while True:
        x = pulse_sensor.normalized_read()
        osc_client.send_message("/pulse", x)
        yield from asyncio.sleep(SAMPLING_DELAY)


def main():
    args = parse_args()
    display.init(rows, cols, sdl=True)

    coros = (
        # pulse_to_osc(args.host, args.port),
        # osc_server(args.host, args.port),
        render(),
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_loop(coros))


if __name__ == '__main__':
    main()
