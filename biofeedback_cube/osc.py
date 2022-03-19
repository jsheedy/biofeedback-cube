import asyncio
from dataclasses import fields
import logging

from pythonosc import dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer, ThreadingOSCUDPServer
from pythonosc import udp_client

from .modes import Modes
from .hydra import hydra


logger = logging.getLogger(__name__)

clients = set()
dsp = dispatcher.Dispatcher()


def update_client(client, name, value):
    ip, port = client
    client = udp_client.SimpleUDPClient(ip, port)
    client.send_message(f'/hydra/{name}', value)


def hydra_callback(hydra, name, value):
    for client in clients:
        if name in ('x', 'y'):
            update_client(client, 'xy', (hydra.x, hydra.y))
        else:
            update_client(client, name, value)


def add_client(client, _addr, args, **kwargs):
    if client not in clients:
        sync_client(client, None, args)
    clients.add(client)


def notify_clients(client, attr, value):
    for c in filter(lambda c: c != client, clients):
        update_client(c, attr, value)


def sync_client(client, _addr, args, **kwargs):
    hydra = args[0]

    # set [a-w] fields
    for field in fields(hydra):
        if field.type is float and len(field.name) == 1 and field.name not in ('x', 'y'):
            update_client(client, field.name, getattr(hydra, field.name))

    update_client(client, 'xy', (hydra.x, hydra.y))


def hydra_xy_handler(client, _addr, args, x, y, **kwargs):
    hydra = args[0]
    hydra.x = x
    hydra.y = y
    notify_clients(client, 'xy', (hydra.x, hydra.y))
    clients.add(client)


def hydra_handler(client, addr, args, value, **kwargs):
    hydra = args[0]
    dim = addr.split('/')[-1]
    setattr(hydra, dim, value)
    notify_clients(client, dim, value)
    clients.add(client)


def hydra_accxyz_handler(_addr, args, x, y, z, **kwargs):
    hydra = args[0]
    hydra.xyz_x = x
    hydra.xyz_y = y
    hydra.xyz_z = z


def midi_note_handler(_addr, args, note, velocity, **kwargs):
    hydra.midi_notes.append(note)


def mode_handler(addr, args, value, **kwargs):
    hydra = args[0]

    mode_l = addr.split('/')
    mode_row = int(mode_l[-2]) - 1
    mode_col = int(mode_l[-1]) - 1
    mode_index = mode_col * 5 + mode_row

    try:
        if mode_index == 24:
            hydra.modes.clear()
        else:
            mode = Modes(mode_index)
            if mode not in hydra.modes:
                logger.info(f'adding hydra mode {mode}')
                hydra.modes[mode] = True
            else:
                logger.info(f'removing hydra mode {mode}')
                del hydra.modes[mode]

    except ValueError:
        logger.error(f'unable to set hydra mode {mode}')


def shutdown_handler(addr, args, value, **kwargs):
    hydra = args[0]
    hydra.shutdown = True


def init():
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
        '/midi/note': midi_note_handler,
        '/mode/*': mode_handler,
        '/shutdown': shutdown_handler,
        '/ping': add_client,
        '*': lambda *args: logger.debug(str(args))
    }

    for pattern, handler in addr_map.items():
        logger.info(f'{pattern}')
        needs_reply_address = handler in (
            sync_client,
            add_client,
            hydra_xy_handler,
            hydra_handler
        )
        dsp.map(pattern, handler, hydra,
                needs_reply_address=needs_reply_address)


@asyncio.coroutine
def async_server(host, port):
    logger.info(f'listening on {host}:{port}')
    loop = asyncio.get_event_loop()
    server = AsyncIOOSCUDPServer((host, port), dsp, loop)
    transport, protocol = yield from server.create_serve_endpoint()
    yield from asyncio.sleep(86400*7)


def server(host, port):
    logger.info(f'listening on {host}:{port}')
    server = ThreadingOSCUDPServer((host, port), dsp)
    server.serve_forever()
