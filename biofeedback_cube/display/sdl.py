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

    def __init__(self, rows, cols, width=900, height=900):
        self.cols = cols
        self.rows = rows
        self.width = width
        self.height = height
        # self.scale = scale

        sdl2.ext.init()
        self.window = sdl2.ext.Window('BIOFEEDBACK CUBE', size=(self.width, self.height))
        self.window.show()
        surface = self.window.get_surface()
        self.pixels = sdl2.ext.pixels2d(surface)
        self.renderer = sdl2.ext.Renderer(surface, flags=sdl2.SDL_RENDERER_ACCELERATED)
        # renderer.blendmode = sdl2.SDL_BLENDMODE_MOD
        self.pixels[:, :] = 0xffffffff
        self.window.refresh()
        self.state = SimpleNamespace(
            running=True,
            paused=False,
            speed=0.000005,
            joystick=SimpleNamespace(
                x=0,
                y=0
            )
        )

        self.keys_down = set()


    def handle_events(self):
        events = sdl2.ext.get_events()
        for event in events:
            logger.debug(event.key.keysym.sym)
            # if event.type == sdl2.SDL_PRESSED:
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == 32:  # space
                    hydra.mode = next(self.mode_iter).value
                elif event.key.keysym.sym == 61:  # +
                    if self.state.speed < 0.001:
                        self.state.speed += 0.0000025
                elif event.key.keysym.sym == 45:  # -
                    self.state.speed -= 0.0000025
                    if self.state.speed < 0:
                        self.state.speed = 0
                elif event.key.keysym.sym == 113:  # q
                    self.state.running = False

                self.keys_down.clear()
                self.keys_down.add(event.key.keysym.sym)
                logging.debug(self.keys_down)

            # elif event.type == sdl2.SDL_RELEASED:
            elif event.type == sdl2.SDL_KEYUP:
                self.keys_down.clear()

            elif event.type == sdl2.SDL_MOUSEMOTION:
                x, y = ctypes.c_int(0), ctypes.c_int(0) # Create two ctypes values
                _ = sdl2.mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
                y_normalized = y.value / self.height
                x_normalized = x.value / self.width

                for key in self.keys_down:
                    setattr(hydra, chr(key), y_normalized)

                hydra.y = y_normalized
                hydra.x = x_normalized

            elif event.type == sdl2.SDL_QUIT:
                self.state.running = False

    def draw(self, grid, brightness=1.0, gamma=1.0):
        self.handle_events()
        if not self.state.running:
            raise exceptions.UserQuit('user quit')

        rgb = (grid * brightness * 255).astype(np.uint32)
        r, g, b = rgb[::-1, ::-1, 1], rgb[::-1, ::-1, 2], rgb[::-1, ::-1, 3]

        # convert to SDL color 32bit BGRA format
        x = 0xff000000 | (r << 16) | (g << 8) | b

        yc = np.linspace(0, self.rows, self.height, endpoint=False, dtype=np.int32)
        xc = np.linspace(0, self.cols, self.width, endpoint=False, dtype=np.int32)
        yy, xx = np.meshgrid(yc, xc)
        self.pixels[:, :] = x[yy, xx]
        _ = sdl2.ext.get_events()
        self.window.refresh()
