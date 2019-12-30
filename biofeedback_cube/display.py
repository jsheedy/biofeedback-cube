import ctypes
import logging
from types import SimpleNamespace

import numpy as np

from biofeedback_cube import exceptions

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

    def __init__(self, rows, cols, width=600, height=600):
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

    def handle_events(self):
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == 32:  # space
                    self.state.paused = not self.state.paused
                elif event.key.keysym.sym == 61:  # +
                    if self.state.speed < 0.001:
                        self.state.speed += 0.0000025
                elif event.key.keysym.sym == 45:  # -
                    self.state.speed -= 0.0000025
                    if self.state.speed < 0:
                        self.state.speed = 0
                elif event.key.keysym.sym == 113:  # q
                    self.state.running = False

            elif event.type == sdl2.SDL_MOUSEMOTION:
                x, y = ctypes.c_int(0), ctypes.c_int(0) # Create two ctypes values
                _ = sdl2.mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
                self.state.joystick.y = y.value / self.height
                self.state.joystick.x = x.value / self.width

            elif event.type == sdl2.SDL_QUIT:
                self.state.running = False

    def draw(self, grid):
        self.handle_events()
        if not self.state.running:
            raise exceptions.UserQuit('user quit')

        rgb = (grid * 255).astype(np.uint32)
        r, g, b = rgb[:, :, 1], rgb[:, :, 2], rgb[:, :, 3]

        # convert to SDL color 32bit BGRA format
        x = 0xff000000 | (r << 16) | (g << 8) | b

        yc = np.linspace(0, self.rows, self.height, endpoint=False, dtype=np.int32)
        xc = np.linspace(0, self.cols, self.width, endpoint=False, dtype=np.int32)
        yy, xx = np.meshgrid(yc, xc)
        self.pixels[:, :] = x[yy, xx]
        _ = sdl2.ext.get_events()
        self.window.refresh()


class DotstarDisplay():
    def __init__(self, width, height, faces=({}, {}, {'flip': True})):
        self.width = width
        self.height = height
        self.faces = faces
        self.strip = Adafruit_DotStar()
        self.strip.begin()

    def serialize_grid(self, grid):
        grid[:, 0::2, :] = grid[::-1, 0::2, :]
        grid[:, :, 1:] = grid[:, :, 3:0:-1]
        return grid.transpose(1, 0, 2).ravel()

    def draw(self, grid, gamma=2.0):
        arr = self.serialize_grid(grid)
        gamma_corrected = np.clip(arr, 0, 1) ** gamma
        # disable gamma correction
        # gamma_corrected = arr

        u8 = (gamma_corrected * 255.0).astype(np.uint8)
        u8[0::4] = 0xff  # dotstar format is (0xff,r,g,b)
        _bytes = u8.tobytes()

        # TODO: implement face flipping
        # all_faces = b''
        # for face in self.faces:
            # if 'flip' in face:
                # all_faces += _bytes[::-1]
            # else:
                # all_faces += _bytes
        # self.strip.show(all_faces)
        self.strip.show(len(self.faces) * _bytes )


def init(rows, cols, sdl=True):
    global _display
    if sdl:
        _display = SDLDisplay(rows, cols)
    else:
        _display = DotstarDisplay(rows, cols)


def draw(grid):
    _display.draw(grid)
