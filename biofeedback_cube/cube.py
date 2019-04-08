#!/usr/bin/env python

import argparse
import asyncio
import importlib
import logging
import os
import time

from dataclasses import dataclass
from pythonosc import udp_client

from biofeedback_cube import osc
from biofeedback_cube import pulse_sensor
from biofeedback_cube import buffer
from biofeedback_cube import display

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SAMPLING_DELAY = 1/20


@dataclass
class Hydra():
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    q: float = 0.0
    pulse: float = 0.0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=37337, help="The port to listen on")
    parser.add_argument("--simulator", action='store_true', help="run simulator")
    parser.add_argument("--reload", action='store_true', help="live coding")
    args = parser.parse_args()
    return args


@asyncio.coroutine
def main_loop(coros):
    done, _pending = yield from asyncio.wait(coros, return_when=asyncio.FIRST_EXCEPTION)
    for t in done:
        if t.exception():
            logger.exception('task exception')
            raise t.exception()


@asyncio.coroutine
def render(rows, cols, reload=False, hydra=None):
    t0 = time.time()
    buff = buffer.Buffer(rows, cols)

    while True:
        t = time.time() - t0
        try:
            if reload:
                importlib.reload(buffer)
            b2 = buffer.Buffer(rows, cols, hydra)
            b2.locals = buff.locals
            buff = b2
            buff.update(t)
            grid = buff.get_grid()
            display.draw(grid)
        except Exception:
            logger.exception('whoops 🙀')
            continue

        yield from asyncio.sleep(0.01)


@asyncio.coroutine
def pulse_to_osc(host, port):

    # osc_client = udp_client.SimpleUDPClient('192.168.0.255', 37337, allow_broadcast=True)
    osc_client = udp_client.SimpleUDPClient(host, port)

    while True:
        x = pulse_sensor.normalized_read()
        osc_client.send_message("/pulse", x)
        yield from asyncio.sleep(SAMPLING_DELAY)


def main():
    rows = 68
    cols = 8

    args = parse_args()
    display.init(rows, cols, sdl=args.simulator)

    reload = args.reload or os.getenv('RELOAD')

    if reload:
        logger.info(f'live coding mode enabled')
    else:
        logger.info(f'live coding mode disabled')

    hydra = Hydra()

    coros = (
        # pulse_to_osc(args.host, args.port),
        render(rows, cols, hydra=hydra, reload=reload),
        osc.server(args.host, args.port, hydra),
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_loop(coros))


if __name__ == '__main__':
    main()
