import logging
import os

import numpy as np


logger = logging.getLogger(__name__)


def bytes_to_str(b1, b2):
    return '{:02x} {:02x}'.format(b1, b2)


def sin(x):
    return (np.sin(x) + 1)/2


def cos(x):
    return (np.cos(x) + 1)/2


def index_dict(d: dict, x: float):
    """ return a value from d for range x 0-1 the best range"""
    keys = list(d.keys())
    index = int(x * len(keys))
    return d[keys[index]]


def shutdown():
    logger.critical("shutting down")
    os.system('sudo shutdown -r now')
