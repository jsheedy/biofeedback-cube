from scipy.signal import sawtooth

from biofeedback_cube.config import HEIGHT, WIDTH
from ..hydra import hydra
from .std import yy, xx


def larson(grid, t):
    strip_height = 10
    y1 = HEIGHT // 2 - strip_height // 2
    y2 = y1 + strip_height
    f = 10.0 * hydra.f
    x = (sawtooth(f*t, width=0.5) + 1) / 2
    xw = int(x * (WIDTH))
    grid[y1:y2, xw, :] = (1, 0, 1)
