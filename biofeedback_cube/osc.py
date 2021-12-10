import asyncio
from functools import partial
from itertools import starmap
import logging
import os

from pythonosc import dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer

# from biofeedback_cube.audio import set_gain


logger = logging.getLogger(__name__)


def hydra_xy_handler(addr, x, y, hydra=None, **kwargs):
    hydra.x = x
    hydra.y = y


def hydra_accxyz_handler(addr, x, y, z, hydra=None, **kwargs):
    hydra.xyz_x = x
    hydra.xyz_y = y
    hydra.xyz_z = z


def hydra_handler(addr, value, hydra=None, **kwargs):
    dim = addr.split('/')[-1]
    setattr(hydra, dim, value)


def play_handler(addr, value, hydra=None, **kwargs):
    hydra.play = bool(value)


def gain_handler(addr, value, hydra=None, **kwargs):
    set_gain(value)
    hydra.gain = value


def pulse_handler(addr, value, hydra=None, **kwargs):
    hydra.pulse = value


def mode_handler(addr, value, hydra=None, **kwargs):
    if int(value) == 1:
        mode_l = addr.split('/')
        mode_row = int(mode_l[-2]) - 1
        mode_col = int(mode_l[-1]) - 1
        mode = mode_col * 3 + mode_row
        logger.info(f'setting hydra mode {mode}')
        hydra.mode = mode 


def shutdown_handler(addr, value, **kwargs):
    logger.critical("shutting down")
    os.system('sudo shutdown -r now')


@asyncio.coroutine
def server(host, port, hydra):

    addr_map = {
        '/play': partial(play_handler, hydra=hydra),
        '/pulse': partial(pulse_handler, hydra=hydra),
        '/hydra/a': partial(hydra_handler, hydra=hydra),
        '/hydra/b': partial(hydra_handler, hydra=hydra),
        '/hydra/c': partial(hydra_handler, hydra=hydra),
        '/hydra/d': partial(hydra_handler, hydra=hydra),
        '/hydra/e': partial(hydra_handler, hydra=hydra),
        '/hydra/xy': partial(hydra_xy_handler, hydra=hydra),
        '/accxyz': partial(hydra_accxyz_handler, hydra=hydra),
        '/mode/*': partial(mode_handler, hydra=hydra),
        '/shutdown': shutdown_handler,
        '*': lambda *args: logger.debug(str(args))
    }

    dsp = dispatcher.Dispatcher()

    logger.info(f'listening on {host}:{port} for ')
    for pattern, handler in addr_map.items():
        logger.info(f'{pattern}')
        dsp.map(pattern, handler)

    loop = asyncio.get_event_loop()
    server = AsyncIOOSCUDPServer((host, port), dsp, loop)
    transport, protocol = yield from server.create_serve_endpoint()
    yield from asyncio.sleep(86400*7)

