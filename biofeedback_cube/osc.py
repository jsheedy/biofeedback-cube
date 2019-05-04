import asyncio
from functools import partial
from itertools import starmap
import logging
import os

from pythonosc import dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer


logger = logging.getLogger(__name__)


def hydra_handler(addr, value, hydra=None, **kwargs):
    dim = addr.split('/')[-1]
    if dim == 'x':
        hydra.x = value
    if dim == 'y':
        hydra.y = value
    if dim == 'z':
        hydra.z = value


def pulse_handler(addr, value, hydra=None, **kwargs):
    hydra.pulse = value


def shutdown_handler(addr, value, **kwargs):
    logger.critical("shutting down")
    os.system('sudo shutdown -r now')


@asyncio.coroutine
def server(host, port, hydra):

    addr_map = {
        # '/pulse': partial(pulse_handler, hydra=hydra),
        '/hydra/*': partial(hydra_handler, hydra=hydra),
        '/shutdown': shutdown_handler,
        '*': lambda *args: logger.debug(str(args))
    }

    dsp = dispatcher.Dispatcher()

    for pattern, handler in addr_map.items():
        dsp.map(pattern, handler)

    loop = asyncio.get_event_loop()
    server = AsyncIOOSCUDPServer((host, port), dsp, loop)
    transport, protocol = yield from server.create_serve_endpoint()
    yield from asyncio.sleep(86400*7)