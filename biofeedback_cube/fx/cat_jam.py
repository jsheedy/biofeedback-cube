import logging
import os
from pathlib import Path

import imageio
import numpy as np

from ..config import WIDTH, HEIGHT
from ..hydra import hydra

logger = logging.getLogger(__name__)

images = []
meta = {}


def open_images():
    path = Path(os.path.dirname(__file__)) / Path('../../assets/cat-jam.gif')
    logger.info(f'opening {path}')
    with imageio.read(path) as f:
        for im in f.iter_data():
            images.append(im.astype(np.float64) / 255)
        meta['length'] = f.get_length()
        meta['duration'] = f.get_meta_data()['duration']
        meta['total_time'] = (meta['length'] * meta['duration']) / 1000


def jam(grid, t):
    pos = (t % meta['total_time']) / meta['total_time']
    length = len(images) - 1
    idx = int(pos * length)
    rgba = images[idx]

    h, w = rgba.shape[:2]

    x_i = np.linspace(0, w, WIDTH, dtype=np.int32)
    y_i = np.linspace(0, h, HEIGHT, dtype=np.int32)

    crop = np.take(np.take(rgba, y_i, axis=0, mode='clip'), x_i, axis=1, mode='clip')
    crop = crop[::-1, ::-1, :]
    im = crop[:, :, :3]
    alpha = crop[:, :, 3:]

    grid[:, :, :] += alpha * im


open_images()
