import math

import numpy as np
from punyty.vector import Vector3
from punyty.objects import Cube
from punyty.renderers import ArrayRenderer
from punyty.scene import Scene

from ..hydra import hydra
from ..utils import sin, cos


scene = Scene()
cube = Cube(color=Vector3(1, 0.8, 0.7), position=Vector3(-.35, 0, 1.3))
scene.add_object(cube)

cache = {}


def get_target_array(grid):
    if 'target_array' in cache:
        return cache.get('target_array')

    h, w, c = grid.shape
    s = max((h, w))
    ta = np.zeros((s, s, c), dtype=np.float32)
    cache['target_array'] = ta
    return ta


def get_renderer(target_array):
    renderer = cache.get('renderer')
    if renderer:
        return renderer

    renderer = ArrayRenderer(
        target_array=target_array,
        draw_edges=False,
        draw_wireframe=False,
        draw_polys=True
    )
    cache['renderer'] = renderer
    return renderer


def punyty(grid, t):
    target_array = get_target_array(grid)
    renderer = get_renderer(target_array)

    if hydra.f < 0.2:
        cube.rotate(Vector3(-3+hydra.a*6, -3+hydra.b*6, -3+hydra.c*6))
        cube.color = Vector3(hydra.a, hydra.b, hydra.c)
    else:
        cube.rotate(Vector3(math.sin(.9*t), math.sin(0.63*t), math.cos(0.85*t)))
        color = Vector3(sin(.1*t + 1), .1 + sin(0.08*t), cos(0.1515*t))
        cube.color = color

    renderer.render(scene)

    grid_w = grid.shape[1]
    target_w = target_array.shape[1]
    xi = np.linspace(0, target_w, grid_w, endpoint=False, dtype=np.int32)
    dst = target_array[:, xi]
    mask = dst > 0
    grid[mask] = dst[mask]