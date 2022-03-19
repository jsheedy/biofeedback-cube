import argparse
import asyncio
import logging
from queue import Queue
import signal
import sys
import threading
import time
import traceback

import uvloop

from biofeedback_cube.buffer import buffer
from biofeedback_cube import config
from biofeedback_cube import display
from biofeedback_cube import exceptions
from biofeedback_cube import osc
from biofeedback_cube import utils
from biofeedback_cube.hydra import hydra, save_hydra

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

queue = Queue(maxsize=2)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=37339, help="The port to listen on")
    parser.add_argument("--simulator", action='store_true', help="run simulator")
    parser.add_argument("--verbose", action='store_true', help="verbose")
    args = parser.parse_args()
    return args


@asyncio.coroutine
def main_loop(coros):
    done, _pending = yield from asyncio.wait(coros, return_when=asyncio.FIRST_COMPLETED)
    for t in done:
        print(f'{t} is done')
        shutdown = hydra.shutdown
        save_hydra()
        if shutdown:
            utils.shutdown()

        if t.exception():
            traceback_str = ''.join(traceback.format_tb(t.exception().__traceback__))
            logger.critical(traceback_str)
            sys.exit(-1)


def render():
    try:
        buffer.update()
        return buffer.buffer

    except exceptions.UserQuit:
        logger.warning('user quit')
        save_hydra()
        raise
    except Exception:
        logger.exception('whoops 🙀')
        raise


@asyncio.coroutine
def async_render():
    while True:
        if hydra.shutdown:
            logger.warning('hydra shutdown, exiting render loop')
            break
        grid = render()
        # grid = grid[::-1, ::-1, ...]
        brightness = hydra.e
        display.draw(grid, brightness=brightness)
        yield from asyncio.sleep(0.010)


def async_main(args):
    coros = (
        async_render(),
        osc.async_server(args.host, args.port),
    )
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_loop(coros))


def thread_render():
    while True:
        grid = render()
        queue.put(grid.copy())


def thread_draw():
    while True:
        logger.debug(f'{queue.qsize()}')
        grid = queue.get()
        display.draw(grid)


def thread_main(args):

    t1 = threading.Thread(target=thread_render, daemon=True)
    t2 = threading.Thread(target=osc.server, args=(args.host, args.port), daemon=True)

    t1.start()
    t2.start()

    thread_draw()


def sigterm_handler(signum, frame):
    logger.warning('caught SIGTERM')
    save_hydra()
    sys.exit(0)


def main():
    args = parse_args()
    signal.signal(signal.SIGTERM, sigterm_handler)
    if args.verbose:
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    osc.init()
    display.init(config.HEIGHT, config.WIDTH, sdl=args.simulator)

    # thread_main(args)
    async_main(args)


if __name__ == '__main__':
    main()
