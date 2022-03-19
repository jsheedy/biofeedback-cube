import numpy as np

from ..config import HEIGHT, WIDTH
from ..hydra import hydra


def midi(grid, t):
    notes = hydra.midi_notes

    # _min, _max = min(notes), max(notes)
    _min, _max = 40, 90
    dynamic_range = _max - _min

    # melody
    for i, (note, velocity, timestamp) in enumerate(notes[0]):
        y = (note - _min) / dynamic_range
        yi = int(y * (HEIGHT - 1))
        grid[yi, WIDTH-1-i] = (0.0, 1.0, 0)

    # metronome
    if notes[1]:
        note, _velocity, timestamp = notes[1][-1]
        bright = np.clip(1 - (t - timestamp), 0, 1)
        grid[:, :] = (0.0, bright, 0)
