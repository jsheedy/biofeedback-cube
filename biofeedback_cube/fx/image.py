import logging
import os
from pathlib import Path

import imageio
from scipy.ndimage import zoom
import numpy as np

from ..config import WIDTH, HEIGHT
from ..hydra import hydra
from ..utils import index_dict

logger = logging.getLogger(__name__)


iix = np.arange(WIDTH, dtype=np.int32)
iiy = np.arange(HEIGHT, dtype=np.int32)

images = []


def open_images():
    path = Path(os.path.dirname(__file__)) / Path('../../assets')
    for p in path.glob('*.png'):
        logger.info(f'opening {p}')
        print(f'opening {p}')
        images.append(open_image(p))


def open_image(path):
    im = imageio.imread(path)
    h, w = im.shape[:2]
    s = 100 / max((h, w))
    im = zoom(im, (s, s, 1))
    return im.astype(np.float64) / 255


def image(grid, t):

    # x0 = int(-40 + 80 * (1-hydra.x))
    # y0 = int(-40 + 80 * (1-hydra.y))

    idx = np.clip(0, len(images), int(hydra.f * len(images)))
    rgba = images[idx]

    im = rgba[:, :, :3]
    im = im[::-1, ::-1, :]

    grid[:, :] = im[:HEIGHT, :WIDTH, :]

    # h, w = im.shape[:2]

    # x_i = np.take(iix, range(x0, x0+w), mode='wrap')
    # y_i = np.take(iiy, range(y0, y0+h), mode='wrap')

    # xx_i, yy_i = np.meshgrid(x_i, y_i, sparse=True)

    # grid[yy_i, xx_i, :] = im


open_images()