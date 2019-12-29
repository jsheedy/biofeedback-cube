import asyncio
from functools import partial
from itertools import starmap
import logging
import os

from pythonosc import dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer


logger = logging.getLogger(__name__)


def hydraxy_handler(addr, x, y, hydra=None, **kwargs):
    hydra.x = x
    hydra.y = y

def hydra_handler(addr, value, hydra=None, **kwargs):
    dim = addr.split('/')[-1]
    if dim == 'a':
        hydra.a = value
    if dim == 'b':
        hydra.b = value
    if dim == 'c':
        hydra.c = value

def pulse_handler(addr, value, hydra=None, **kwargs):
    hydra.pulse = value


def shutdown_handler(addr, value, **kwargs):
    logger.critical("shutting down")
    os.system('sudo shutdown -r now')


@asyncio.coroutine
def server(host, port, hydra):

    addr_map = {
        # '/pulse': partial(pulse_handler, hydra=hydra),
        '/hydra/a': partial(hydra_handler, hydra=hydra),
        '/hydra/b': partial(hydra_handler, hydra=hydra),
        '/hydra/c': partial(hydra_handler, hydra=hydra),
        '/hydra/xy': partial(hydraxy_handler, hydra=hydra),
        '/shutdown': shutdown_handler,
        '*': lambda *args: logger.info(str(args))
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
