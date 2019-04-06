#!/usr/bin/env python

import asyncio

import numpy as np
from pythonosc import udp_client

client = udp_client.SimpleUDPClient('localhost', 37337, allow_broadcast=True)

@asyncio.coroutine
def sweep():
    N = 100
    vals = np.linspace(0, 1, N)
    while True:
        for x in vals:
            client.send_message("/pulse", x)
            print(f'/pulse')
            yield from asyncio.sleep(0.05)


def main():
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(sweep())
    loop.run_forever()

if __name__ == "__main__":
    main()
