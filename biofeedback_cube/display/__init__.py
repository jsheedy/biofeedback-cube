from .dotstar import DotstarDisplay
from .sdl import SDLDisplay

_display = None


def init(rows, cols, sdl=True):
    global _display
    if sdl:
        _display = SDLDisplay(rows, cols)
    else:
        _display = DotstarDisplay(rows, cols)


def draw(grid, brightness=1.0):
    _display.draw(grid, brightness=brightness)
