import numpy as np

from ..state import clock
from ..config import HEIGHT, WIDTH
from ..hydra import hydra
from ..palettes import palettes, cmap
from ..state import midi_notes
from ..utils import index_dict, xx, yy, sin, cos


def note_default(grid, t):

    # _min, _max = min(notes), max(notes)
    _min, _max = 40, 90
    dynamic_range = _max - _min

    if midi_notes.notes[0]:
        for i, (note, velocity, timestamp) in enumerate(midi_notes.notes[0]):
            y = (note - _min) / dynamic_range
            yi = int(y * (HEIGHT - 1))
            grid[yi, i % WIDTH] = (0.0, 1.0, 0)


def note_tunnel(grid, t):
    palette = index_dict(palettes, hydra.a)

    if midi_notes.notes[0]:
        for i, (note, velocity, timestamp) in enumerate(midi_notes.notes[0]):
            age = np.clip(1 - (t - timestamp), 0, 1)
            x = 0.5 + (1 - age) * np.cos(2 * np.pi * (note / 12))
            y = 0.5 + (1 - age) * np.sin(2 * np.pi * (note / 12))

            r = 4.01 * 1 / age
            cone = np.clip(1-np.sqrt((r*(xx-x))**2 + (r*(yy-y))**2), 0, 1)
            mask = cone > 0
            grid[mask] = cmap(palette, cone)[mask]


def metronome_default(grid, t):
    if midi_notes.notes[1]:
        note, _velocity, timestamp = midi_notes.notes[1][-1]
        bright = np.clip(1 - (t - timestamp), 0, 1)
        grid[:2, :] = (0.0, bright, 0)
        grid[-2:, :] = (0.0, bright, 0.0)
        grid[-2:, :] = (1.0, bright, 1.0)


NOTE_MODES = {
    'default': note_default,
    'tunnel': note_tunnel
}

METRONOME_MODES = {
    'default': metronome_default
}


def midi(grid, t):

    midi_notes.bleed()
    note_handler = index_dict(NOTE_MODES, hydra.f)
    note_handler(grid, t)

    metronome_handler = index_dict(METRONOME_MODES, hydra.g)
    metronome_handler(grid, t)
