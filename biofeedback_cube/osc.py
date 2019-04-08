import asyncio
from functools import partial
from itertools import starmap
import logging
import os

from pythonosc import dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer


logger = logging.getLogger(__name__)


def hydra_handler(addr, value, hydra=None, **kwargs):
    hydra.x = value


def pulse_handler(addr, value, hydra=None, **kwargs):
    hydra.pulse = value


def shutdown_handler(addr, value, **kwargs):
    logger.critical("shutting down")
    os.system('sudo shutdown -r now')


@asyncio.coroutine
def server(host, port, hydra):

    addr_map = {
        '/pulse': partial(pulse_handler, hydra=hydra),
        '/hydra/*': partial(hydra_handler, hydra=hydra),
        '/shutdown': shutdown_handler,
        '*': logger.debug
    }

    dsp = dispatcher.Dispatcher()

    all(starmap(dsp.map, addr_map.items()))

    loop = asyncio.get_event_loop()
    server = AsyncIOOSCUDPServer((host, port), dsp, loop)
    asyncio.ensure_future(server.create_serve_endpoint())
