#!/usr/bin/env python

import argparse
import asyncio
import concurrent
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

from biofeedback_cube.audio import play_sample
from biofeedback_cube import exceptions
from biofeedback_cube import osc
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
    play: bool = True
    gain: float = 0.0
    mode: int = 8
    last_update: float = 0

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name not in ('last_update', 'pulse'):
            self.last_update = time.time() - t0


ROWS = 68
COLS = 8

hydra = Hydra()
buff = buffer.Buffer(ROWS, COLS, hydra=hydra)


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
    while True:
        grid = render(rows, cols, reload=reload)
        display.draw(grid)
        yield from asyncio.sleep(0.002)


def process_render(rows, cols, reload=False):
    while True:
        grid = render(rows, cols, reload=reload)
        queue.put(grid)


def process_draw():
    while True:
        grid = queue.get()
        display.draw(grid)


@asyncio.coroutine
def audio(hydra):
    while True:
        if hydra.play:
            executor = concurrent.futures.ProcessPoolExecutor()
            # executor = concurrent.futures.ThreadPoolExecutor()
            fname = '/home/pi/Music/lowAsharp2.wav'
            loop = asyncio.get_event_loop()
            task = loop.run_in_executor(executor, play_sample, fname)
            while not task.done() and hydra.play:
                yield from asyncio.sleep(.1)
            if not task.done():
                task.cancel()
            executor.shutdown(wait=False)
        yield from asyncio.sleep(.1)


def async_main(rows, cols, args):
    coros = (
        # audio(hydra),
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
    display.init(ROWS, COLS, sdl=args.simulator)

    reload = args.reload or os.getenv('RELOAD')

    if reload:
        logger.info(f'live coding mode enabled')
    else:
        logger.info(f'live coding mode disabled')

    # process_main(rows, cols, args.reload)
    async_main(ROWS, COLS, args)


if __name__ == '__main__':
    main()
