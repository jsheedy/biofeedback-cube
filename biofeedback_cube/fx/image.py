import logging
import os
from pathlib import Path

import imageio
import numpy as np

from ..config import WIDTH, HEIGHT
from ..hydra import hydra
from ..utils import sin

logger = logging.getLogger(__name__)

images = []


def open_images():
    path = Path(os.path.dirname(__file__)) / Path('../../assets')
    for p in path.glob('*.png'):
        logger.info(f'opening {p}')
        images.append(open_image(p))


def open_image(path):
    im = imageio.imread(path)
    h, w = im.shape[:2]
    return im.astype(np.float64) / 255


def image(grid, t):

    r, g, b = hydra.a, hydra.b, hydra.c
    idx = int(hydra.f * (len(images)-1))
    rgba = images[idx]

    im = rgba[:, :, :3]
    im = im[::-1, ::-1, :]

    h, w = im.shape[:2]

    x = 2 * hydra.x - 1
    y = 2 * hydra.y - 1

    if hydra.i >= .5:
        scale = hydra.g * 2
    else:
        scale = .95 + .2 * sin(3 * t)

    # crop out a region of the image, in the size of the target grid repeating
    # or dropping pixels where necessary.

    x1 = round(w * x + (w - scale * w) / 2)
    x2 = round(x1 + w * scale)

    y1 = round(h * y + (h - scale * h) / 2)
    y2 = round(y1 + h * scale)

    x_i = np.linspace(x1, x2, WIDTH, dtype=np.int32)
    y_i = np.linspace(y1, y2, HEIGHT, dtype=np.int32)
    xx_i, yy_i = np.meshgrid(x_i, y_i, sparse=True)

    crop = np.take(np.take(im, y_i, axis=0, mode='clip'), x_i, axis=1, mode='clip')

    # set mask for areas outside image
    mask = np.invert(np.squeeze((xx_i < 0) | (xx_i > w) | (yy_i < 0) | (yy_i > h)))
    grid[mask] = (crop * (r, g, b))[mask]



open_images()
