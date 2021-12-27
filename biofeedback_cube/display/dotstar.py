import logging
logger = logging.getLogger(__name__)

import numpy as np  # noqa: E402
try:
    from dotstar import Adafruit_DotStar  # noqa: E402
except ImportError:
    logger.info('unable to import Adafruit_DotStar')


class DotstarDisplay():
    def __init__(self, _width, _height):
        self.strip = Adafruit_DotStar()
        self.strip.begin()

    def serialize_grid(self, grid):
        # flip display on x/y, RGB->BGR
        grid[:, :, 1:] = grid[::-1, ::-1, 3:0:-1]

        # invert every other column since display is laid out in Z-order
        grid[:, 1::2, :] = grid[::-1, 1::2, :]

        # transpose so ravel outputs colors first, then rows, then cols
        return np.swapaxes(grid, 0, 1).ravel()

    def draw(self, grid, brightness=1.0, gamma=2.0):
        arr = self.serialize_grid(grid)
        arr *= brightness
        gamma_corrected = np.clip(arr, 0, 1) ** gamma

        u8 = (gamma_corrected * 255.0).astype(np.uint8)
        u8[0::4] = 0xff  # dotstar format is (0xff,r,g,b)
        _bytes = u8.tobytes()

        self.strip.show(_bytes)
