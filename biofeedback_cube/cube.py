import argparse
import asyncio
import importlib
import logging
from multiprocessing import Process, Queue
import signal
import sys
import time
import traceback

import uvloop

from biofeedback_cube import buffer
from biofeedback_cube import config
from biofeedback_cube import display
from biofeedback_cube import exceptions
from biofeedback_cube import osc
from biofeedback_cube import utils
from biofeedback_cube.hydra import hydra, save_hydra

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SAMPLING_DELAY = 1/20

t0 = time.time()

queue = Queue()

buff = buffer.Buffer(config.HEIGHT, config.WIDTH)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=37339, help="The port to listen on")
    parser.add_argument("--simulator", action='store_true', help="run simulator")
    parser.add_argument("--reload", action='store_true', help="live coding")
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


def render(reload=False):
    t = time.time() - t0
    try:
        if reload:
            # global buff
            # importlib.reload(buffer)
            from biofeedback_cube.fx import larson
            importlib.reload(larson)
        buff.update(t)
        return buff.buffer

    except exceptions.UserQuit:
        logger.warning('user quit')
        save_hydra()
        raise
    except Exception:
        logger.exception('whoops 🙀')
        raise


@asyncio.coroutine
def async_render(reload=False):
    while True:
        if hydra.shutdown:
            logger.warning('hydra shutdown, exiting render loop')
            break
        grid = render(reload=reload)
        yield from asyncio.sleep(0.010)
        brightness = hydra.e
        display.draw(grid, brightness=brightness)
        yield from asyncio.sleep(0.010)


def process_render(rows, cols, reload=False):
    while True:
        grid = render(reload=reload)
        queue.put(grid)


def process_draw():
    while True:
        grid = queue.get()
        display.draw(grid)


def async_main(args):
    coros = (
        async_render(reload=args.reload),
        osc.server(args.host, args.port, hydra),
    )
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_loop(coros))


def process_main(rows, cols, reload):

    p1 = Process(target=process_render, args=(rows, cols), kwargs={'reload': reload})
    p2 = Process(target=process_draw)
    p1.start()
    p2.start()
    p1.join()
    p2.join()


def sigterm_handler(signum, frame):
    logger.warning('caught SIGTERM')
    save_hydra()
    sys.exit(0)


def main():
    args = parse_args()
    signal.signal(signal.SIGTERM, sigterm_handler)
    if args.verbose:
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger = logging.getLogger(__name__)

    display.init(config.HEIGHT, config.WIDTH, sdl=args.simulator)

    # process_main(ROWS, COLS, args.reload)
    async_main(args)


if __name__ == '__main__':
    main()
