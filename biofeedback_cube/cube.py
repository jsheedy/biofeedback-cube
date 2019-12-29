#!/usr/bin/env python

import argparse
import asyncio
import importlib
import logging
from multiprocessing import Process, Queue
import os
import sys
import time
import traceback

from dataclasses import dataclass
from pythonosc import udp_client
import uvloop

from biofeedback_cube import exceptions
from biofeedback_cube import osc
from biofeedback_cube import pulse_sensor
from biofeedback_cube import buffer
from biofeedback_cube import display

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SAMPLING_DELAY = 1/20

t0 = time.time()
queue = Queue()


@dataclass
class Hydra():
    x: float = 0.5
    y: float = 0.5
    z: float = 0.5
    a: float = 0.5
    b: float = 0.5
    c: float = 0.5
    pulse: float = 0.5

rows = 68
cols = 8

hydra = Hydra()
buff = buffer.Buffer(rows, cols, hydra=hydra)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=37339, help="The port to listen on")
    parser.add_argument("--simulator", action='store_true', help="run simulator")
    parser.add_argument("--reload", action='store_true', help="live coding")
    args = parser.parse_args()
    return args


@asyncio.coroutine
def main_loop(coros):
    done, _pending = yield from asyncio.wait(coros, return_when=asyncio.FIRST_EXCEPTION)
    for t in done:
        print(f'{t} is done')
        if t.exception():
            traceback_str = ''.join(traceback.format_tb(t.exception().__traceback__))
            logger.critical(traceback_str)
            sys.exit(-1)


def render(rows, cols, reload=False):
    
    t = time.time() - t0
    try:
        if reload:
            global buff
            importlib.reload(buffer)
            b2 = buffer.Buffer(rows, cols, hydra)
            b2.locals = buff.locals
            buff = b2
        buff.update(t)
        return buff.get_grid()

    except exceptions.UserQuit:
        raise
    except Exception:
        logger.exception('whoops 🙀')


@asyncio.coroutine
def async_render(rows, cols, reload=False):
    # _t0 = time.time()
    while True:
        grid = render(rows, cols, reload=reload)
        display.draw(grid)
        # t = time.time()
        # dt = t-_t0
        # _t0 = t
        # print(dt)
        yield from asyncio.sleep(0.005)


def process_render(rows, cols, reload=False):
    # _t0 = time.time()
    while True:
        grid = render(rows, cols, reload=reload)
        queue.put(grid)
        # t = time.time()
        # dt = t-_t0
        # _t0 = t
        # print(dt)

def process_draw():
    while True:
        grid = queue.get()
        display.draw(grid)

@asyncio.coroutine
def pulse_to_osc(host, port):

    # osc_client = udp_client.SimpleUDPClient('192.168.0.255', 37337, allow_broadcast=True)
    osc_client = udp_client.SimpleUDPClient(host, port)

    while True:
        x = pulse_sensor.normalized_read()
        osc_client.send_message("/pulse", x)
        yield from asyncio.sleep(SAMPLING_DELAY)


def async_main(rows, cols, args):
    coros = (
        # pulse_to_osc(args.host, args.port),
        async_render(rows, cols, reload=args.reload),
        osc.server(args.host, args.port, hydra),
    )
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_loop(coros))
 
def process_main(rows, cols, reload):

    p1 = Process(target=process_render, args=(rows, cols), kwargs={'reload':reload})
    p2 = Process(target=process_draw)
    p1.start()
    p2.start()
    p1.join()
    p2.join()



def main():
    args = parse_args()
    display.init(rows, cols, sdl=args.simulator)

    reload = args.reload or os.getenv('RELOAD')

    if reload:
        logger.info(f'live coding mode enabled')
    else:
        logger.info(f'live coding mode disabled')

    # process_main(rows, cols, args.reload)
    async_main(rows, cols, args)

if __name__ == '__main__':
    main()
