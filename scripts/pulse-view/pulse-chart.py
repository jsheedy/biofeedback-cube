"""
realtime plot OSC pulse
"""

import argparse
import asyncio
import collections
import math

from matplotlib import pyplot as plt

from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server


BUF_LEN = 80
buffer = collections.deque([0]*BUF_LEN, BUF_LEN)


def pulse_handler(addr, val):
    buffer.append(val)
    plot()


def plot():
    plt.clf()
    plt.plot(buffer)
    plt.draw()
    plt.pause(0.001)
    # plt.show()


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="0.0.0.0", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=37339, help="The port to listen on")
    args = parser.parse_args()

    plt.ion()
    # plt.show()

    dispatcher = Dispatcher()
    dispatcher.map("/pulse", pulse_handler)

    loop = asyncio.get_event_loop()
    server = osc_server.AsyncIOOSCUDPServer( (args.ip, args.port), dispatcher, loop)
    # server = osc_server.ThreadingOSCUDPServer( (args.ip, args.port), dispatcher)
    # server.serve()
    transport, protocol = await server.create_serve_endpoint()
    await asyncio.sleep(10**30)


if __name__ == "__main__":
    asyncio.run(main())
