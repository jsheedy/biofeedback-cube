import imageio
import numpy as np
from biofeedback_cube.fx.palette import palettes

w = 600
h = 200


for name, p in palettes.items():
    target = np.zeros((h, w, 3))
    print(name)
    x = np.arange(0, w)
    xp = np.linspace(0, w-1, (p.shape[0]))

    r = np.interp(x, xp, p[:, 0])
    g = np.interp(x, xp, p[:, 1])
    b = np.interp(x, xp, p[:, 2])

    target[:, :] = np.array((r, g, b)).T

    imageio.imwrite(f'palettes/{name}.png', target)
