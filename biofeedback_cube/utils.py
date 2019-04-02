import numpy as np


def bytes_to_str(b1, b2):
    return '{:02x} {:02x}'.format(b1, b2)


def sin(x):
    return (np.sin(x) + 1)/2


def cos(x):
    return (np.cos(x) + 1)/2


def decimate(x):
    """ make x smaller by doing piecewise mean """
    return x