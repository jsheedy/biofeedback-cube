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
            flipped_im = im[::-1, ::-1, :]
            images.append(flipped_im.astype(np.float64) / 255)
        meta['length'] = f.get_length()
        meta['duration'] = f.get_meta_data()['duration']
        meta['total_time'] = (meta['length'] * meta['duration']) / 1000

    meta['h'], meta['w'] = im.shape[:2]
    meta['x_i'] = np.linspace(0, meta['w'], WIDTH, dtype=np.int32)
    meta['y_i'] = np.linspace(0, meta['h'], HEIGHT, dtype=np.int32)


def jam(grid, t):
    pos = (t % meta['total_time']) / meta['total_time']
    length = len(images) - 1
    idx = int(pos * length)
    rgba = images[idx]

    crop = np.take(np.take(rgba, meta['y_i'], axis=0, mode='clip'), meta['x_i'], axis=1, mode='clip')
    im = crop[:, :, :3]
    alpha = crop[:, :, 3:]

    mask = np.squeeze(alpha > 0)

    grid[mask, :] = im[mask]


open_images()
