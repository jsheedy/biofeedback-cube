import asyncio
from functools import partial
from itertools import starmap
import logging
import os

from pythonosc import dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc import udp_client

logger = logging.getLogger(__name__)


def update_client(client, name, value):
    ip, port = client
    client = udp_client.SimpleUDPClient(ip, port)
    client.send_message(f'/hydra/{name}', value)


def hydra_xy_handler(addr, args, x, y, **kwargs):
    hydra = args[0]
    hydra.x = x
    hydra.y = y


def hydra_accxyz_handler(addr, args, x, y, z, **kwargs):
    hydra = args[0]
    hydra.xyz_x = x
    hydra.xyz_y = y
    hydra.xyz_z = z


def hydra_handler(client, addr, args, value, **kwargs):
    hydra = args[0]
    dim = addr.split('/')[-1]
    setattr(hydra, dim, value)
    hydra.clients.add(client)


def add_client(client, addr, args, **kwargs):
    hydra = args[0]
    hydra.clients.add(client)


def mode_handler(addr, args, value, **kwargs):
    hydra = args[0]
    if int(value) == 1:
        mode_l = addr.split('/')
        mode_row = int(mode_l[-2]) - 1
        mode_col = int(mode_l[-1]) - 1
        mode = mode_col * 3 + mode_row
        logger.info(f'setting hydra mode {mode}')
        hydra.mode = mode


def shutdown_handler(addr, args, value, **kwargs):
    hydra = args[0]
    logger.critical("shutting down")
    hydra.shutdown = True
    os.system('sudo shutdown -r now')


@asyncio.coroutine
def server(host, port, hydra):

    addr_map = {
        '/hydra/a': hydra_handler,
        '/hydra/b': hydra_handler,
        '/hydra/c': hydra_handler,
        '/hydra/d': hydra_handler,
        '/hydra/e': hydra_handler,
        '/hydra/f': hydra_handler,
        '/hydra/g': hydra_handler,
        '/hydra/h': hydra_handler,
        '/hydra/i': hydra_handler,
        '/hydra/j': hydra_handler,
        '/hydra/k': hydra_handler,
        '/hydra/l': hydra_handler,
        '/hydra/m': hydra_handler,
        '/hydra/xy': hydra_xy_handler,
        '/accxyz': hydra_accxyz_handler,
        '/mode/*': mode_handler,
        '/shutdown': shutdown_handler,
        '/ping': add_client,
        '*': lambda *args: logger.debug(str(args))
    }

    dsp = dispatcher.Dispatcher()

    logger.info(f'listening on {host}:{port} for ')
    for pattern, handler in addr_map.items():
        logger.info(f'{pattern}')
        dsp.map(pattern, handler, hydra, needs_reply_address=(handler in (add_client, hydra_handler)))

    loop = asyncio.get_event_loop()
    server = AsyncIOOSCUDPServer((host, port), dsp, loop)
    transport, protocol = yield from server.create_serve_endpoint()
    yield from asyncio.sleep(86400*7)

