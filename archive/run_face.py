""" CODE MOVED TO display module """
1/0

#!/usr/bin/env python
import os
import importlib
import time

import numpy as np

import face


def as_uint8(arr, gamma=2.0):

    gamma_corrected = np.clip(arr, 0, 1) ** gamma
    u8 = (gamma_corrected * 255.0).astype(np.uint8)
    u8[0::4] = 0xff  # dotstar format is (0xff,r,g,b)
    return u8.tobytes()

    # interpolate from buffer resolution to device resolution
    # r = np.interp(self.device_x, self.buffer_x, buff[:,0]) * 255
    # g = np.interp(self.device_x, self.buffer_x, buff[:,1]) * 255
    # b = np.interp(self.device_x, self.buffer_x, buff[:,2]) * 255

    # device_buffer = np.vstack((r,g,b)).T
    # return device_buffer.astype(np.uint8).tobytes()


def render_dotstar(strip, arr):
    arr_bytes = as_uint8(arr)
    strip.show(arr_bytes)


def main(render_sdl):
    if render_sdl:
        from sdl.driver import sdl_init
        from sdl.driver import sdl_draw
        window, renderer, pixels = sdl_init()

    else:
        from dotstar import Adafruit_DotStar
        strip = Adafruit_DotStar()
        strip.begin()

    t0 = time.time()
    i = 0

    while True:
        t = time.time() - t0
        i += 1
        try:
            importlib.reload(face)
            f = face.Face()
            f.render(t=t, i=i)
        except (ModuleNotFoundError):
            continue

        if render_sdl:
            print('rendering sdl')
            sdl_draw(pixels, window, f.grid)
        else:
            arr = face.to_arr()
            render_dotstar(strip, arr)

if __name__ == "__main__":
    RENDER_SDL = os.getenv('SDL', False)
    main(RENDER_SDL)
