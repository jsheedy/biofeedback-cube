import ctypes
import itertools
import logging
from types import SimpleNamespace

import numpy as np

from biofeedback_cube import exceptions
from biofeedback_cube.hydra import hydra
from biofeedback_cube.modes import Modes


logger = logging.getLogger(__name__)

try:
    import sdl2
    import sdl2.ext
except ImportError:
    logger.info('unable to import sdl2')


class SDLDisplay():
    mode_iter = itertools.cycle(Modes)

    def __init__(self, rows, cols, width=512, height=512):
        self.width = width
        self.height = height
        yc = np.linspace(0, rows, height, endpoint=False, dtype=np.int32)
        xc = np.linspace(0, cols, width, endpoint=False, dtype=np.int32)
        self.yy, self.xx = np.meshgrid(yc, xc)

        sdl2.ext.init()
        self.window = sdl2.ext.Window('BIOFEEDBACK CUBE', size=(width, height), position=(0, 0))
        self.window.show()
        surface = self.window.get_surface()
        self.pixels = sdl2.ext.pixels2d(surface)
        self.renderer = sdl2.ext.Renderer(surface, flags=sdl2.SDL_RENDERER_ACCELERATED)
        self.window.refresh()

        self.state = SimpleNamespace(
            running=True,
            speed=0.000005,
        )

        self.keys_down = set()

    def handle_events(self):
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_KEYDOWN:
                logger.info(f'keydown {event.key.keysym.sym}')
                if event.key.keysym.sym == 32:  # space
                    mode = next(self.mode_iter)
                    hydra.modes = {mode: True}
                    logger.info(f'switched to mode {hydra.modes}')
                elif event.key.keysym.sym == 61:  # +
                    pass
                elif event.key.keysym.sym == 45:  # -
                    pass
                elif event.key.keysym.sym == 113:  # q
                    self.state.running = False
                elif event.key.keysym.sym == 48:  # 0
                    hydra.zero()

                self.keys_down.clear()
                self.keys_down.add(event.key.keysym.sym)

            # elif event.type == sdl2.SDL_RELEASED:
            elif event.type == sdl2.SDL_KEYUP:
                self.keys_down.clear()

            elif event.type == sdl2.SDL_MOUSEMOTION:
                x, y = ctypes.c_int(0), ctypes.c_int(0)  # Create two ctypes values
                _ = sdl2.mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
                y_normalized = (y.value + 1) / self.height
                x_normalized = (x.value + 1) / self.width

                for key in self.keys_down:
                    setattr(hydra, chr(key), y_normalized)

                hydra.y = y_normalized
                hydra.x = x_normalized

            elif event.type == sdl2.SDL_QUIT:
                self.state.running = False

    def draw(self, grid, brightness=1.0, gamma=1.0):
        self.handle_events()

        if not self.state.running:
            raise exceptions.UserQuit

        rgb = (grid * brightness * 255).astype(np.uint32)
        r, g, b = rgb[:, :, 1], rgb[:, :, 2], rgb[:, :, 3]

        # convert to SDL color 32bit BGRA format
        x = 0xff000000 | (r << 16) | (g << 8) | b

        self.pixels[...] = x[self.yy, self.xx]
        self.window.refresh()
