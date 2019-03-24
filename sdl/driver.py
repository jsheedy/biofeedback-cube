"""
SDL NCEP Reanalysis browser
joseph.sheedy@gmail.com

data from
ftp://ftp.cdc.noaa.gov/Datasets/ncep.reanalysis/pressure/
https://www.esrl.noaa.gov/psd/data/gridded/data.ncep.reanalysis.html
ftp://ftp.cdc.noaa.gov/Datasets/ncep.reanalysis/pressure/hgt.2018.nc
"""

import ctypes
import functools
import importlib
import os
import sys
from types import SimpleNamespace
import time

import matplotlib
import numpy as np
import sdl2.ext
import xarray

# import get_grid


SCALE= 10
# ROWS = 30
# COLS = 50
ROWS = 68
COLS = 8
WIDTH = COLS * SCALE
HEIGHT = ROWS * SCALE


def normalize(grid):
    """ normalize grid to (0,1) """
    field = grid.T
    min_h, max_h = field.min(), field.max()
    return (field - min_h) / (max_h - min_h)

def sdl_draw(pixels, window, grid):
    rgb = (grid * 255).astype(np.uint32)
    r,g,b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]

    # convert to SDL color 32bit BGRA format
    x = 0xff000000 | (r << 16) | (g << 8) | b
    # scale up to window size
    x = np.repeat(x, SCALE, axis=1)
    x = np.repeat(x, SCALE, axis=0)
    pixels[:,:] = x.T

    events = sdl2.ext.get_events()
    window.refresh()
    sdl2.SDL_Delay(0)


def handle_events(state):
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym == 32:  # space
                state.paused = not state.paused
            elif event.key.keysym.sym == 61:  # +
                if state.speed < 0.001:
                    state.speed += 0.0000025
            elif event.key.keysym.sym == 45:  # -
                state.speed -= 0.0000025
                if state.speed < 0:
                    state.speed = 0
            elif event.key.keysym.sym == 113:  # q
                state.running = False

        elif event.type == sdl2.SDL_MOUSEMOTION:
            x, y = ctypes.c_int(0), ctypes.c_int(0) # Create two ctypes values
            _buttonstate = sdl2.mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
            state.joystick.y = y.value / HEIGHT
            state.joystick.x = x.value / WIDTH
            if not state.paused:
                state.t = state.joystick.y

        elif event.type == sdl2.SDL_QUIT:
            state.running = False
            break


def sdl_init():
    sdl2.ext.init()
    window = sdl2.ext.Window("reanalyis", size=(WIDTH, HEIGHT))
    window.show()
    surface = window.get_surface()
    pixels = sdl2.ext.pixels2d(surface)
    renderer = sdl2.ext.Renderer(surface, flags=sdl2.SDL_RENDERER_ACCELERATED)
    # renderer.blendmode = sdl2.SDL_BLENDMODE_MOD
    return window, renderer, pixels


def render():

    window, renderer, pixels = sdl_init()

    pixels[:,:] = 0xffffffff

    state = SimpleNamespace(
        running=True,
        paused=True,
        speed=0.000005,
        t=0,
        l=0,
        joystick = SimpleNamespace(
            x=0,
            y=0
        )
    )
    t0 = time.time()
    while state.running:
        handle_events(state)
        if not state.paused:
            state.t += state.speed
            state.t = state.t % 1

        # grid = np.random.random((COLS,ROWS,3)) # np.mgrid[100:100] # ds['hgt'][t,state.l]
        t = time.time() - t0
        try:
            importlib.reload(get_grid)
            grid = get_grid.get_grid(COLS, ROWS, t, state.joystick)
            sdl_draw(pixels, renderer, grid)
        except (ModuleNotFoundError, Exception):
            continue
        window.refresh()

        sdl2.SDL_Delay(5)

    sdl2.ext.quit()


if __name__ == "__main__":
    render()
