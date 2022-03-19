from ..config import HEIGHT, WIDTH
from ..hydra import hydra


def midi(grid, t):
    notes = hydra.midi_notes

    if not notes:
        return

    while len(notes) > 8:
        notes.popleft()

    # _min, _max = min(notes), max(notes)
    _min, _max = 40, 90
    dynamic_range = _max - _min

    for i, note in enumerate(notes):
        y = (note - _min) / dynamic_range
        yi = int(y * (HEIGHT - 1))
        grid[yi, WIDTH-1-i] = (0.0, 1.0, 0)
