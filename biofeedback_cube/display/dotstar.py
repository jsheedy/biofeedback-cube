import logging
logger = logging.getLogger(__name__)

import numpy as np  # noqa: E402
try:
    from dotstar import Adafruit_DotStar  # noqa: E402
except ImportError:
    logger.info('unable to import Adafruit_DotStar')


class DotstarDisplay():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.strip = Adafruit_DotStar()
        self.strip.begin()

    def serialize_grid(self, grid):
        # views were causing mirror images on flipped columns
        # when assigning to self
        # FIXME: remove the copies

        # RGB->BGR
        g = np.copy(grid)
        g[:, :, 1:] = grid[:, :, 3:0:-1]

        # invert every other column for Biofeedback Cube Mark 1
        # which is laid out in Z-order
        g[:, 1::2, :] = np.copy(g[::-1, 1::2, :])

        # transpose so ravel outputs colors first, then rows, then cols
        # could use .transpose(1, 0, 2) instead
        return np.swapaxes(g, 0, 1).ravel()

    def draw(self, grid, brightness=1.0, gamma=2.0):
        arr = self.serialize_grid(grid)
        arr *= brightness
        gamma_corrected = np.clip(arr, 0, 1) ** gamma
        # disable gamma correction
        # gamma_corrected = arr

        u8 = (gamma_corrected * 255.0).astype(np.uint8)
        u8[0::4] = 0xff  # dotstar format is (0xff,r,g,b)
        _bytes = u8.tobytes()

        self.strip.show(_bytes)
