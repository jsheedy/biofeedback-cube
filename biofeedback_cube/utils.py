import functools
import os

import imageio
import numpy as np
from scipy.ndimage.interpolation import zoom


def bytes_to_str(b1, b2):
    return '{:02x} {:02x}'.format(b1, b2)


def sin(x):
    return (np.sin(x) + 1)/2


def cos(x):
    return (np.cos(x) + 1)/2


def decimate(x):
    """ make x smaller by doing piecewise mean """
    return x

@functools.lru_cache()
def open_image(fname, scale=None):
    path = os.path.join(os.path.dirname(__file__), '../assets', fname)
    im = imageio.imread(path)
    if scale:
        im = zoom(im, (scale, scale, 1))

    return im.astype(np.float64) / 255
