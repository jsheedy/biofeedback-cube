import asyncio
import logging

import numpy as np

logger = logging.getLogger(__name__)

try:
    import sdl2
    import sdl2.ext
except ImportError:
    logger.info('unable to import sdl2')

try:
    from dotstar import Adafruit_DotStar
except ImportError:
    logger.info('unable to import Adafruit_DotStar')


_display = None


class SDLDisplay():

    def __init__(self, rows, cols, scale=10):
        self.width = cols * scale
        self.height = rows * scale
        self.scale = scale

        sdl2.ext.init()
        self.window = sdl2.ext.Window('BIOFEEDBACK CUBE', size=(self.width, self.height))
        self.window.show()
        surface = self.window.get_surface()
        self.pixels = sdl2.ext.pixels2d(surface)
        self.renderer = sdl2.ext.Renderer(surface, flags=sdl2.SDL_RENDERER_ACCELERATED)
        # renderer.blendmode = sdl2.SDL_BLENDMODE_MOD
        self.pixels[:, :] = 0xffffffff
        self.window.refresh()

    def draw(self, grid):
        rgb = (grid * 255).astype(np.uint32)
        r, g, b = rgb[:, :, 1], rgb[:, :, 2], rgb[:, :, 3]

        # convert to SDL color 32bit BGRA format
        x = 0xff000000 | (r << 16) | (g << 8) | b
        # scale up to window size
        x = np.repeat(x, self.scale, axis=1)
        x = np.repeat(x, self.scale, axis=0)
        self.pixels[:, :] = x.T
        _ = sdl2.ext.get_events()
        self.window.refresh()


class DotstarDisplay():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.strip = Adafruit_DotStar()
        self.strip.begin()

    def serialize_grid(self, grid):
        grid[:, 0::2, :] = grid[::-1, 0::2, :]
        return grid.transpose(1, 0, 2).ravel()

    def draw(self, grid, gamma=2.0):
        arr = self.serialize_grid(grid)
        gamma_corrected = np.clip(arr, 0, 1) ** gamma
        u8 = (gamma_corrected * 255.0).astype(np.uint8)
        u8[0::4] = 0xff  # dotstar format is (0xff,r,g,b)
        self.strip.show(u8.tobytes())


def init(rows, cols, sdl=True):
    global _display
    if sdl:
        _display = SDLDisplay(rows, cols)
    else:
        _display = DotstarDisplay(rows, cols)


def draw(grid):
    _display.draw(grid)
