import functools
import logging
import os

import imageio
import numpy as np
from scipy.ndimage.interpolation import zoom

from biofeedback_cube import config


logger = logging.getLogger(__name__)


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
        aspect = config.WIDTH / config.HEIGHT
        im = zoom(im, (scale, scale * aspect * config.ASPECT, 1))

    return im.astype(np.float64) / 255


def shutdown():
    logger.critical("shutting down")
    os.system('sudo shutdown -r now')
